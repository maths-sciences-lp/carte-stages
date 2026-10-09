"""Ajoute aux données publiées les établissements des codes NAF nouvellement entrés dans domaines.py.

Sans refaire la collecte nationale, en trois phases demandées explicitement :
1. stock : SIRET du stock Sirene (millésime donné) dont l'unité légale a l'un des codes demandés,
   actifs, diffusibles, hors entrepreneurs individuels, unité employeuse ;
2. api : chaque SIRET revérifié par l'API Recherche d'entreprises avec les règles de la collecte
   (stage_rattrapage.admissible), réponses gardées en cache ;
3. ecrire : stage_donnees.preparer département par département (types, seuils, copies, règles de
   nom), entreprises liquidées (liquidations-bodacc.json) écartées, lignes AJOUTÉES aux fichiers
   publiés (aucune ligne existante remplacée), catalogues et bilans recalculés ; --write pour écrire.

python3 source/stage_nouveaux_codes.py --cache CACHE --codes 41.10A 41.10C --phase stock \
  --url-etablissements URL --url-unites URL
python3 source/stage_nouveaux_codes.py --cache CACHE --phase api
python3 source/stage_nouveaux_codes.py --cache CACHE --phase ecrire --root /copie/carte-stages-donnees [--write]
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time

from stage_collecte import CODES, EFFECTIFS, ROOT, atomic_json, configurer_cache
from stage_rattrapage import Rattrapage
from stage_donnees import catalogue_formations, fichier, preparer
from stage_catalogues import ecrire_catalogues


def lire(path):
    return json.loads(Path(path).read_text())


def phase_stock(args):
    import duckdb
    if set(args.codes) - set(CODES):
        raise SystemExit('Codes absents de domaines.py : ' + ' '.join(sorted(set(args.codes) - set(CODES))))
    allowed = {d for a in lire(ROOT/'commun/academies.json') for d in a['deps']}
    con = duckdb.connect()
    con.execute('INSTALL httpfs; LOAD httpfs;')
    rows = con.execute(f"""
        SELECT e.siret, e.codeCommuneEtablissement FROM read_parquet(?) e JOIN read_parquet(?) u ON u.siren = e.siren
        WHERE u.activitePrincipaleUniteLegale IN ({','.join('?' * len(args.codes))})
          AND e.etatAdministratifEtablissement = 'A' AND u.etatAdministratifUniteLegale = 'A'
          AND u.categorieJuridiqueUniteLegale <> '1000'
          AND e.statutDiffusionEtablissement = 'O' AND u.statutDiffusionUniteLegale = 'O'
          AND u.trancheEffectifsUniteLegale IN ({','.join('?' * len(EFFECTIFS))})""",
        [args.url_etablissements, args.url_unites, *args.codes, *EFFECTIFS]).fetchall()
    cibles = defaultdict(list)
    for siret, commune in rows:
        dep = (commune or '')[:3] if (commune or '').startswith('97') else (commune or '')[:2]
        if dep in allowed:
            cibles[dep].append(siret)
    atomic_json(args.cache/'cibles.json', dict(codes=args.codes, stock=[args.url_etablissements, args.url_unites],
                                                date=time.strftime('%Y-%m-%d'),
                                                cibles={d: sorted(s) for d, s in sorted(cibles.items())}))
    print(json.dumps(dict(siret=sum(len(s) for s in cibles.values()), departements=len(cibles))))


def phase_api(args):
    cibles = lire(args.cache/'cibles.json')['cibles']
    collector = Rattrapage(args.cache, args.rate)
    items = [(d, s) for d, ss in cibles.items() for s in ss]
    bilan = Counter()
    with ThreadPoolExecutor(4) as pool:
        for i, value in enumerate(pool.map(collector.verifier_siret, items), 1):
            bilan['gardes' if value['rows'] else 'rejetes'] += 1
            bilan.update(value['rejets'])
            if i % 500 == 0:
                print(i, '/', len(items), dict(bilan), flush=True)
    print(json.dumps(dict(bilan, requetes=collector.requests, erreurs=dict(collector.errors)), ensure_ascii=False))


def phase_ecrire(args):
    root = args.root.resolve()
    if args.write and subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() in ('main', 'master', ''):
        raise SystemExit('Écriture réservée à une branche de travail')
    cibles = lire(args.cache/'cibles.json')['cibles']
    liquidees = {j['siret'][:9] for j in lire(root/'liquidations-bodacc.json')['details']} \
        if (root/'liquidations-bodacc.json').exists() else set()
    catalog = lire(root/'catalogue.json')
    ajouts, bilan, exclus = {}, Counter(), Counter()
    for dep, sirets in sorted(cibles.items()):
        rows = []
        for s in sirets:
            path = args.cache/'temoin'/dep/(s+'.json')
            if path.exists():
                rows += [r for r in lire(path)['rows'] if r['s'][:9] not in liquidees]
        groups, ex = preparer(rows)
        exclus.update(ex)
        for k, lignes in groups.items():
            path = root/'sirene'/dep/(k+'.json')
            existants = lire(path) if path.exists() else []
            vus = {r[7] for r in existants}
            nouveaux = [r for r in lignes if r[7] not in vus]
            if nouveaux:
                ajouts[(dep, k)] = sorted(existants + nouveaux)
                bilan[k] += len(nouveaux)
    print(json.dumps(dict(ajouts=dict(bilan.most_common()), total=sum(bilan.values()), exclus=dict(exclus)),
                     ensure_ascii=False, indent=1))
    if not args.write:
        return
    for (dep, k), rows in ajouts.items():
        catalog['departements'][dep]['secteurs'][k] = fichier(root/'sirene'/dep/(k+'.json'), rows)
    code = catalogue_formations()
    catalog['domaines'] = [dict(d, s=[dict(s, c=sum(x['secteurs'][s['k']]['n'] for x in catalog['departements'].values()
                                                       if s['k'] in x['secteurs'])) for s in d['s']]) for d in code['domaines']]
    catalog['formations'] = code['formations']
    catalog['version'] = hashlib.sha256(json.dumps(catalog['departements'], sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json', catalog)
    ecrire_catalogues(root)
    deps = {dep for dep, _ in ajouts}
    b = lire(root/'bilan.json')
    for e in b['departements']:
        if e['dep'] in deps:
            files = catalog['departements'][e['dep']]['secteurs']
            e['lignes'] = sum(v['n'] for v in files.values())
            e['bytes'] = sum(v['bytes'] for v in files.values()) + catalog['departements'][e['dep']]['lycees']['bytes']
    atomic_json(root/'bilan.json', b)
    sizepath = root/'tailles-fichiers.csv'
    with sizepath.open(newline='') as f:
        tailles = {r['fichier']: r for r in csv.DictReader(f)}
    for dep, k in ajouts:
        name = f'sirene/{dep}/{k}.json'
        tailles[name] = dict(fichier=name, octets=(root/name).stat().st_size, lignes=len(ajouts[(dep, k)]))
    with sizepath.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fichier', 'octets', 'lignes'], lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(tailles.values(), key=lambda r: r['fichier']))
    atomic_json(root/args.rapport, dict(date=time.strftime('%Y-%m-%d'), codes=lire(args.cache/'cibles.json')['codes'],
                                         stock=lire(args.cache/'cibles.json')['stock'],
                                         ajouts=dict(bilan.most_common()), exclus=dict(exclus)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--phase', choices=['stock', 'api', 'ecrire'], required=True)
    p.add_argument('--codes', nargs='+')
    p.add_argument('--url-etablissements')
    p.add_argument('--url-unites')
    p.add_argument('--rate', type=float, default=5)
    p.add_argument('--root', type=Path)
    p.add_argument('--rapport', default='nouveaux-codes.json')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    configurer_cache(args.cache)
    if args.phase == 'stock':
        if not (args.codes and args.url_etablissements and args.url_unites):
            p.error('--codes, --url-etablissements et --url-unites sont obligatoires')
        phase_stock(args)
    elif args.phase == 'api':
        phase_api(args)
    else:
        if not args.root:
            p.error('--root est obligatoire')
        phase_ecrire(args)


if __name__ == '__main__':
    main()
