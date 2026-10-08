"""Extrait départemental du stock officiel par lectures HTTP partielles mesurées.

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

from stage_stock_config import configuration, departements, extrait, espace_libre
from stage_collecte import CODES, atomic_json, configurer_cache

BASE = 'https://static.data.gouv.fr/resources/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/'
URLS = {
    'etablissements': BASE+'20261001-073823/stock-stocketablissement-parquet.parquet',
    'unites': BASE+'20261001-073325/stock-stockunitelegale-parquet.parquet',
}


def now():
    return datetime.now(timezone.utc).isoformat()


class PartialReader:
    def __init__(self, cache, budget, urls=None):
        self.cache, self.budget = cache, budget
        self.urls = urls or URLS
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
                if key not in parent.urls:
                    self.send_error(404); return
                if shutil.disk_usage(parent.cache).free < 2_000_000_000:
                    self.send_error(507, 'Less than 2 GB free; safe stop'); return
                headers = {'User-Agent': 'CarteStages/1.0 (temoin departemental)', 'Accept-Encoding': 'identity'}
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
                    req = urllib.request.Request(parent.urls[key], headers=headers, method='GET' if get else 'HEAD')
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
    parser.add_argument('--departements', nargs='+')
    parser.add_argument('--date-stock')
    parser.add_argument('--url-etablissements')
    parser.add_argument('--url-unites')
    args = parser.parse_args()
    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    if args.departements:
        deps=sorted(set(args.departements))
        if not all(re.fullmatch(r'(?:[0-9]{2,3}|2[AB])',d) for d in deps):
            parser.error('Codes département invalides')
        if not all((args.date_stock,args.url_etablissements,args.url_unites)):
            parser.error('Date et deux URL du stock obligatoires pour un nouveau périmètre')
        urls={'etablissements':args.url_etablissements,'unites':args.url_unites}
        if not all(u.startswith(BASE) and u.endswith('.parquet') for u in urls.values()):
            parser.error('Utiliser les stocks officiels HTTPS de data.gouv.fr')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',args.date_stock) or any(u[len(BASE):len(BASE)+8]!=args.date_stock.replace('-','') for u in urls.values()):
            parser.error('La date déclarée doit correspondre aux deux URL du millésime')
        configurer_cache(cache)
        cfg=dict(departements=deps,date_stock=args.date_stock,urls=urls,suffixe='extrait',
                 empreinte_naf=hashlib.sha256('\n'.join(CODES).encode()).hexdigest())
        conf=cache/'configuration-stock.json'
        if conf.exists() and json.loads(conf.read_text())!=cfg:
            raise ValueError('Cache associé à un autre périmètre ou stock')
        atomic_json(conf,cfg)
    if not args.departements and not (cache/'configuration-stock.json').exists() and not (cache/'stock-etablissements-provenance.json').exists():
        parser.error('Un nouveau cache exige un périmètre, une date et les URL du stock explicites')
    cfg=configuration(cache)
    output = extrait(cache,args.phase)
    if output.exists():
        print('Extrait existant conservé :', output); return
    if shutil.disk_usage(cache).free < 2_000_000_000:
        raise RuntimeError('Moins de 2 Go libres : extraction reportée')
    reader = PartialReader(cache,args.budget_mo*1_000_000,cfg.get('urls'))
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
    report = dict(source=reader.urls[args.phase],stock=cfg['date_stock'],departements=departements(cache),
                  debut=reader.started,duckdb=duckdb.__version__)
    try:
        if args.phase == 'etablissements':
            query = """SELECT siret, siren, etatAdministratifEtablissement,
                statutDiffusionEtablissement, activitePrincipaleEtablissement,
                nomenclatureActivitePrincipaleEtablissement, trancheEffectifsEtablissement,
                codeCommuneEtablissement, coordonneeLambertAbscisseEtablissement,
                coordonneeLambertOrdonneeEtablissement
                FROM read_parquet($src) WHERE CASE WHEN starts_with(codeCommuneEtablissement,'97') OR starts_with(codeCommuneEtablissement,'98') THEN substr(codeCommuneEtablissement,1,3) ELSE substr(codeCommuneEtablissement,1,2) END IN (SELECT unnest($deps))"""
            conn.execute('COPY ('+query+") TO $dest (FORMAT PARQUET, COMPRESSION ZSTD)",{"src":url,"dest":str(temp),"deps":departements(cache)})
        else:
            etab = extrait(cache,'etablissements')
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
