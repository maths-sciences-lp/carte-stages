"""Collecte nationale reprenable, région par région, sans données de personnes.

Le mode historique de telecharger.py reste inchangé. Les réponses de l'API ne
sont jamais archivées telles quelles : seuls les champs utiles des personnes
morales diffusibles et des établissements actifs géolocalisés sont conservés.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import threading
import time
import urllib.parse

from domaines import DOMAINES

ROOT = Path(__file__).resolve().parents[1]
API = 'https://recherche-entreprises.api.gouv.fr/search'
EFFECTIFS = '01,02,03,11,12,21,22,31,32,41,42,51,52,53'.split(',')
CODES = sorted({c for ss in DOMAINES.values() for cc in ss.values() for c in cc})
USER_AGENT = 'CarteStages/1.0 (donnees publiques; maths-sciences-lp/carte-stages)'


def dep_commune(code):
    code = str(code or '').upper()
    return code[:3] if code.startswith(('97', '98')) else code[:2]


def conserver(h, e, dep, exclusions):
    if h.get('nature_juridique') == '1000':
        exclusions['entrepreneur_individuel'] += 1
        return
    if h.get('statut_diffusion') != 'O' or e.get('statut_diffusion_etablissement') != 'O':
        exclusions['non_diffusible'] += 1
        return
    if e.get('etat_administratif') != 'A' or dep_commune(e.get('commune')) != dep:
        exclusions['ferme_ou_autre_departement'] += 1
        return
    try:
        lat, lon = float(e.get('latitude')), float(e.get('longitude'))
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180) or (lat, lon) == (0, 0):
            raise ValueError()
    except (TypeError, ValueError):
        exclusions['sans_position'] += 1
        return
    # Même priorité que le générateur historique : activité de l'établissement,
    # puis activité interrogée. Le lot regroupe des codes ; le code de l'unité
    # légale sert de repli explicite, jamais un code arbitraire du lot.
    q = h.get('activite_principale')
    c = e.get('activite_principale') or q
    if c not in CODES and q not in CODES:
        exclusions['activite_non_resolue'] += 1
        return
    return dict(s=e['siret'], n=h['nom_complet'], e=', '.join(e.get('liste_enseignes') or []),
                c=c, q=q, ad=e.get('adresse'), la=lat, lo=lon,
                t=h.get('tranche_effectif_salarie'), nj=h.get('nature_juridique'),
                du=h['statut_diffusion'], de=e['statut_diffusion_etablissement'],
                r=bool(e.get('liste_rge')), dep=dep)


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.part')
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')
    tmp.replace(path)


def configurer_cache(cache):
    """Aucun mélange silencieux avec une collecte faite avant les ajouts France."""
    fingerprint = hashlib.sha256('\n'.join(CODES).encode()).hexdigest()
    path = cache/'configuration-collecte.json'
    if path.exists():
        config = json.loads(path.read_text())
        if config.get('codes_naf') != CODES or config.get('empreinte_naf') != fingerprint:
            raise ValueError('Ce cache correspond à une autre liste de codes NAF')
    else:
        if cache.exists() and any(cache.iterdir()):
            raise ValueError('Cache non vide sans provenance : choisir un nouveau dossier')
        atomic_json(path, dict(codes_naf=CODES, empreinte_naf=fingerprint,
                    cree_le=datetime.now(timezone.utc).isoformat(), source=API))


class Collector:
    def __init__(self, cache, rate):
        self.cache = cache
        self.interval = 1 / rate
        self.lock = threading.Lock()
        self.next_request = 0
        self.requests = 0

    def get(self, params):
        url = API + '?' + urllib.parse.urlencode(params)
        for attempt in range(8):
            with self.lock:
                delay = max(0, self.next_request - time.monotonic())
                if delay:
                    time.sleep(delay)
                self.next_request = time.monotonic() + self.interval
                self.requests += 1
            # Pas de dirigeants dans la réponse ; pas de journal des résultats.
            result = subprocess.run(['curl', '-sS', '--max-time', '60', '-A', USER_AGENT,
                                     '-w', '\n%{http_code}', url], capture_output=True, text=True)
            try:
                body, status = result.stdout.rsplit('\n', 1)
                if status == '200':
                    value = json.loads(body)
                    if isinstance(value.get('results'), list):
                        return value
                if status in ('400', '401', '403', '404'):
                    raise ValueError('API HTTP ' + status)
            except (json.JSONDecodeError, ValueError) as err:
                if str(err).startswith('API HTTP'):
                    raise
            time.sleep(min(120, 5 * 2 ** attempt))
        raise RuntimeError('API indisponible après reprises ; cache conservé')

    def page(self, dep, codes, effectifs, page):
        params = dict(activite_principale=','.join(codes), departement=dep,
                      etat_administratif='A', tranche_effectif_salarie=','.join(effectifs),
                      per_page=25, page=page, limite_matching_etablissements=100,
                      minimal='true', include='matching_etablissements')
        key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
        path = self.cache / 'pages' / dep / (key + '.json')
        if path.exists():
            return json.loads(path.read_text())
        result = self.get(params)
        total = int(result['total_results'])
        # L'API peut plafonner le compteur lui-même à 10 000 : égalité comprise.
        if total >= 10000:
            return dict(total=total, rows=[], exclusions={})
        rows, excluded = [], Counter()
        for company in result['results']:
            entries = company.get('matching_etablissements') or []
            n = 1
            while True:
                for entry in entries:
                    row = conserver(company, entry, dep, excluded)
                    if row:
                        rows.append(row)
                if len(entries) < 100:
                    break
                n += 1
                extra = self.get(dict(params, q=company['siren'], page=1, page_etablissements=n))
                exact = [h for h in extra['results'] if h['siren'] == company['siren']]
                if len(exact) != 1:
                    raise RuntimeError('Pagination des établissements non résolue')
                entries = exact[0].get('matching_etablissements') or []
                if n > 1000:
                    raise RuntimeError('Pagination des établissements excessive')
        value = dict(total=total, pages=int(result['total_pages']), page=page,
                     rows=rows, exclusions=dict(excluded), collected_at=datetime.now(timezone.utc).isoformat())
        atomic_json(path, value)
        return value

    def departement(self, dep):
        path = self.cache / 'departements' / (dep + '.json')
        if path.exists():
            return json.loads(path.read_text())['bilan']
        rows, exclusions = {}, Counter()
        first_dates, pages = [], 0

        def lot(codes, effectifs):
            nonlocal pages
            first = self.page(dep, codes, effectifs, 1)
            if first['total'] >= 10000:
                if len(codes) > 1:
                    mid = len(codes) // 2
                    lot(codes[:mid], effectifs)
                    lot(codes[mid:], effectifs)
                elif len(effectifs) > 1:
                    mid = len(effectifs) // 2
                    lot(codes, effectifs[:mid])
                    lot(codes, effectifs[mid:])
                else:
                    raise RuntimeError('Plafond API atteint : ' + dep + '/' + codes[0])
                return
            for number in range(1, max(1, first['pages']) + 1):
                value = first if number == 1 else self.page(dep, codes, effectifs, number)
                if value['total'] >= 10000:
                    raise RuntimeError('Le lot a dépassé le plafond pendant la collecte')
                pages += 1
                first_dates.append(value['collected_at'])
                exclusions.update(value['exclusions'])
                for row in value['rows']:
                    rows[row['s']] = row
                if pages % 100 == 0:
                    print(f'{dep} : {pages} pages, {len(rows)} établissements conservés', flush=True)

        lot(CODES, EFFECTIFS)
        bilan = dict(dep=dep, etablissements=len(rows), pages=pages, exclusions=dict(exclusions),
                     debut=min(first_dates), fin=max(first_dates))
        atomic_json(path, dict(bilan=bilan, rows=sorted(rows.values(), key=lambda r: r['s'])))
        print(f'{dep} TERMINÉ : {len(rows)} établissements, {pages} pages', flush=True)
        return bilan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--academies', nargs='+', default=['toutes'])
    fingerprint = hashlib.sha256('\n'.join(CODES).encode()).hexdigest()
    parser.add_argument('--cache', type=Path,
                        default=Path.home()/('.cache/carte-stages-national-naf-'+fingerprint[:12]))
    parser.add_argument('--rate', type=float, default=4, help='Maximum global de requêtes/s, <= 6')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 0 < args.rate <= 6 or not 1 <= args.workers <= 6:
        parser.error('Débit > 0 et <= 6 ; 1 à 6 travailleurs')
    academies = json.loads((ROOT/'commun/academies.json').read_text())
    slugs = {a['slug'] for a in academies}
    if args.academies != ['toutes'] and set(args.academies) - slugs:
        parser.error('Académie inconnue')
    regions = {}
    priority = ['lyon', 'lille', 'aix-marseille', 'rennes', 'la-reunion']
    academies.sort(key=lambda a: priority.index(a['slug']) if a['slug'] in priority else 100)
    for ac in academies:
        if args.academies == ['toutes'] or ac['slug'] in args.academies:
            regions.setdefault(ac['region'], []).extend(ac['deps'])
    configurer_cache(args.cache.resolve())
    collector = Collector(args.cache.resolve(), args.rate)
    results = []
    for region, deps in regions.items():
        print('RÉGION : ' + region, flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            results.extend(pool.map(collector.departement, dict.fromkeys(deps)))
    atomic_json(args.cache/'bilan-collecte.json', dict(source=API, departements=results,
                requetes_cette_execution=collector.requests, codes=CODES, effectifs=EFFECTIFS))
    print('COLLECTE TERMINÉE', flush=True)


if __name__ == '__main__':
    main()
