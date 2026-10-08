"""Écoles publiques : les sortir de « Mairies, administrations » dans les données publiées.

Même règle que stage_donnees.preparer (domaines.ECOLES_NAF) : un établissement rangé dans
« Mairies, administrations » dont l'activité propre est 85.10Z ou 85.20Z passe dans
« Écoles maternelles et élémentaires ». Cette catégorie est reliée aux mêmes formations que
les mairies, sauf géomètre et bâtiment (domaines.ECOLES_EXCLUES). Les badges La bonne
alternance suivent l'établissement. Aucun établissement n'est retiré.

L'activité de chaque établissement vient du stock Sirene de l'Insee (fichier siret,naf), par
exemple avec DuckDB sur le parquet public, en ne lisant que les colonnes utiles :
  SELECT siret, activitePrincipaleEtablissement AS naf FROM read_parquet('<stock-stocketablissement-parquet.parquet>')
  WHERE siret IN (SIRET de sirene/*/mairies-administrations.json)

python3 source/stage_ecoles.py --root /copie/carte-stages-donnees --naf siret-naf.csv [--write]
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time

from domaines import ECOLES_EXCLUES, ECOLES_NAF
from stage_collecte import atomic_json
from stage_donnees import fichier
from stage_catalogues import ecrire_catalogues

MAIRIES, ECOLES = 'mairies-administrations', 'ecoles-maternelles-et-elementaires'
NOM = 'Écoles maternelles et élémentaires'


def lire(path):
    return json.loads(Path(path).read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--naf', type=Path, required=True, help='CSV siret,naf (activité de l’établissement)')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.write and subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() in ('main', 'master', ''):
        p.error('Écriture réservée à une branche de travail')
    naf = {r['siret']: r['naf'] for r in csv.DictReader(args.naf.open())}
    catalog = lire(root/'catalogue.json')
    if any(s['k'] == ECOLES for d in catalog['domaines'] for s in d['s']):
        p.error('Catégorie des écoles déjà présente : rien à faire')
    split, sans_code, bilan = {}, 0, dict(deplaces=0, restes=0, par_naf={})
    for dep in sorted(catalog['departements']):
        if MAIRIES not in catalog['departements'][dep]['secteurs']:
            continue
        rows = lire(root/'sirene'/dep/(MAIRIES+'.json'))
        ecoles = [r for r in rows if naf.get(r[7]) in ECOLES_NAF]
        sans_code += sum(1 for r in rows if r[7] not in naf)
        split[dep] = ([r for r in rows if naf.get(r[7]) not in ECOLES_NAF], ecoles)
        bilan['deplaces'] += len(ecoles)
        bilan['restes'] += len(rows) - len(ecoles)
        for r in ecoles:
            bilan['par_naf'][naf[r[7]]] = bilan['par_naf'].get(naf[r[7]], 0) + 1
    bilan['sans_code_insee'] = sans_code
    print(json.dumps(bilan, ensure_ascii=False))
    if not args.write:
        return
    meta = lire(root/'lba/meta.json')
    for dep, (reste, ecoles) in split.items():
        secteurs = catalog['departements'][dep]['secteurs']
        secteurs[MAIRIES] = fichier(root/'sirene'/dep/(MAIRIES+'.json'), reste)
        secteurs[ECOLES] = fichier(root/'sirene'/dep/(ECOLES+'.json'), ecoles)
        src = root/'lba'/dep/(MAIRIES+'.json')
        if src.exists():
            d = lire(src)
            moves = {r[7]: d.pop(r[7]) for r in ecoles if r[7] in d}
            if moves:
                atomic_json(src, d)
                atomic_json(root/'lba'/dep/(ECOLES+'.json'), moves)
                if ECOLES not in meta['files'].get(dep, []):
                    meta['files'][dep] = sorted(meta['files'].get(dep, []) + [ECOLES])
    atomic_json(root/'lba/meta.json', meta)
    for d in catalog['domaines']:
        ks = [s['k'] for s in d['s']]
        if MAIRIES in ks:
            d['s'].insert(ks.index(MAIRIES)+1, dict(n=NOM, k=ECOLES, c=0))
        for s in d['s']:
            s['c'] = sum(x['secteurs'][s['k']]['n'] for x in catalog['departements'].values() if s['k'] in x['secteurs'])
    for f in catalog['formations']:
        if MAIRIES in f['s'] and f['k'] not in ECOLES_EXCLUES:
            i = f['s'].index(MAIRIES)
            f['s'] = f['s'][:i+1] + [ECOLES] + f['s'][i+1:]
    catalog['version'] = hashlib.sha256(json.dumps(catalog['departements'], sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json', catalog)
    ecrire_catalogues(root)
    b = lire(root/'bilan.json')
    for e in b['departements']:
        if e['dep'] in split:
            files = catalog['departements'][e['dep']]['secteurs']
            e['lignes'] = sum(v['n'] for v in files.values())
            e['bytes'] = sum(v['bytes'] for v in files.values()) + catalog['departements'][e['dep']]['lycees']['bytes']
    atomic_json(root/'bilan.json', b)
    sizepath = root/'tailles-fichiers.csv'
    with sizepath.open(newline='') as f:
        rows = list(csv.DictReader(f))
    known = {r['fichier'] for r in rows}
    for r in rows:
        if r['fichier'].endswith('/'+MAIRIES+'.json'):
            path = root/r['fichier']
            r['octets'], r['lignes'] = path.stat().st_size, len(lire(path))
    for dep in split:
        name = f'sirene/{dep}/{ECOLES}.json'
        if name not in known:
            path = root/name
            rows.append(dict(fichier=name, octets=path.stat().st_size, lignes=len(lire(path))))
    with sizepath.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fichier', 'octets', 'lignes'], lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r['fichier']))
    atomic_json(root/'ecoles-hors-mairies.json', dict(date=time.strftime('%Y-%m-%d'), regle=dict(naf=ECOLES_NAF, formations_sans_ecoles=ECOLES_EXCLUES), bilan=bilan))


if __name__ == '__main__':
    main()
