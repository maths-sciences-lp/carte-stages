"""Extrait Créteil du stock officiel par lectures HTTP partielles mesurées.

Ne sauvegarde jamais les stocks nationaux. Le relais local refuse tout GET sans
Range et toute réponse autre que 206. Aucun nom de personne n'est sélectionné.
Python isolé avec duckdb et pyproj ; phase d'extraction indépendante du collecteur.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import threading
import time
import urllib.request

BASE = 'https://static.data.gouv.fr/resources/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/'
URLS = {
    'etablissements': BASE+'20261001-073823/stock-stocketablissement-parquet.parquet',
    'unites': BASE+'20261001-073325/stock-stockunitelegale-parquet.parquet',
}


def now():
    return datetime.now(timezone.utc).isoformat()


class PartialReader:
    def __init__(self, cache, budget):
        self.cache, self.budget = cache, budget
        self.lock = threading.Lock()
        self.bytes = self.reserved = self.requests = 0
        self.started = now()

    def handler(self):
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_HEAD(self):
                self.forward(False)

            def do_GET(self):
                self.forward(True)

            def forward(self, get):
                key = self.path.strip('/').removesuffix('.parquet')
                if key not in URLS:
                    self.send_error(404); return
                headers = {'User-Agent': 'CarteStages/1.0 (temoin Creteil)', 'Accept-Encoding': 'identity'}
                size = 0
                if get:
                    rg = self.headers.get('Range', '')
                    match = re.fullmatch(r'bytes=(\d+)-(\d+)', rg)
                    if not match:
                        self.send_error(400, 'Explicit bounded Range required'); return
                    start, end = map(int, match.groups())
                    size = end-start+1
                    with parent.lock:
                        if size <= 0 or size > 64*1024**2 or parent.reserved+size > parent.budget:
                            self.send_error(413, 'Transfer budget exceeded'); return
                        parent.reserved += size
                    headers['Range'] = rg
                received = 0
                status = None
                error = None
                try:
                    req = urllib.request.Request(URLS[key], headers=headers, method='GET' if get else 'HEAD')
                    with urllib.request.urlopen(req, timeout=90) as response:
                        status = response.status
                        if get and (status != 206 or int(response.headers.get('Content-Length', '-1')) != size):
                            raise ValueError('Server did not honor bounded range')
                        self.send_response(status)
                        for name in ('Content-Length', 'Content-Range', 'Accept-Ranges', 'ETag', 'Last-Modified', 'Content-Type'):
                            if response.headers.get(name): self.send_header(name, response.headers[name])
                        self.end_headers()
                        if get:
                            while received < size:
                                chunk = response.read(min(256*1024, size-received))
                                if not chunk: break
                                received += len(chunk)
                                self.wfile.write(chunk)
                except Exception as exc:
                    error = type(exc).__name__+': '+str(exc)
                    if status is None:
                        self.send_error(502)
                finally:
                    with parent.lock:
                        parent.bytes += received
                        parent.requests += 1
                        with (parent.cache/'stock-requetes.jsonl').open('a') as f:
                            f.write(json.dumps(dict(date=now(),stock=key,range=headers.get('Range'),
                                bytes=received,status=status,erreur=error))+'\n')

        return Handler


def main():
    import duckdb
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--phase', choices=URLS, required=True)
    parser.add_argument('--budget-mo', type=int, default=1300)
    args = parser.parse_args()
    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    output = cache/('stock-'+args.phase+'-creteil.parquet')
    if output.exists():
        print('Extrait existant conservé :', output); return
    if shutil.disk_usage(cache).free < 2_000_000_000:
        raise RuntimeError('Moins de 2 Go libres : extraction reportée')
    reader = PartialReader(cache,args.budget_mo*1_000_000)
    server = ThreadingHTTPServer(('127.0.0.1',0),reader.handler())
    threading.Thread(target=server.serve_forever,daemon=True).start()
    conn = duckdb.connect()
    conn.execute('LOAD httpfs')
    conn.execute("SET memory_limit='384MB'")
    conn.execute('SET threads=3')
    conn.execute("SET max_temp_directory_size='256MB'")
    conn.execute("SET temp_directory=?",[str(cache/'duckdb-temp')])
    url = f'http://127.0.0.1:{server.server_port}/{args.phase}.parquet'
    temp = output.with_suffix('.part')
    started = time.monotonic()
    report = dict(source=URLS[args.phase],stock='2026-10-01',departements=['77','93','94'],
                  debut=reader.started,duckdb=duckdb.__version__)
    try:
        if args.phase == 'etablissements':
            query = """SELECT siret, siren, etatAdministratifEtablissement,
                statutDiffusionEtablissement, activitePrincipaleEtablissement,
                nomenclatureActivitePrincipaleEtablissement, trancheEffectifsEtablissement,
                codeCommuneEtablissement, coordonneeLambertAbscisseEtablissement,
                coordonneeLambertOrdonneeEtablissement
                FROM read_parquet($src) WHERE substr(codeCommuneEtablissement,1,2) IN ('77','93','94')"""
            conn.execute('COPY ('+query+") TO $dest (FORMAT PARQUET, COMPRESSION ZSTD)",{"src":url,"dest":str(temp)})
        else:
            etab = cache/'stock-etablissements-creteil.parquet'
            conn.execute('CREATE TEMP TABLE candidats AS SELECT DISTINCT siren FROM read_parquet(?)',[str(etab)])
            query = """SELECT siren, etatAdministratifUniteLegale, statutDiffusionUniteLegale,
                categorieJuridiqueUniteLegale, activitePrincipaleUniteLegale,
                nomenclatureActivitePrincipaleUniteLegale, trancheEffectifsUniteLegale,
                dateDernierTraitementUniteLegale
                FROM read_parquet($src) SEMI JOIN candidats USING(siren)"""
            conn.execute('COPY ('+query+") TO $dest (FORMAT PARQUET, COMPRESSION ZSTD)",{"src":url,"dest":str(temp)})
        count, unique = conn.execute('SELECT count(*),count(DISTINCT '+('siret' if args.phase=='etablissements' else 'siren')+') FROM read_parquet(?)',[str(temp)]).fetchone()
        if count != unique or not count: raise ValueError('Extrait vide ou clés dupliquées')
        temp.replace(output)
        report.update(lignes=count,octets_fichier=output.stat().st_size,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),succes=True)
    finally:
        server.shutdown()
        report.update(fin=now(),duree_secondes=round(time.monotonic()-started,3),octets_transferes=reader.bytes,requetes_http=reader.requests)
        (cache/('stock-'+args.phase+'-provenance.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
