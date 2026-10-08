"""Applique aux données publiées les découpages et les lieux sans personnel de domaines.py.

Mêmes règles que stage_donnees.preparer, sans refaire la collecte :
- découpage (domaines.DECOUPAGES) : un établissement d'une catégorie d'origine passe dans la
  nouvelle catégorie quand son activité (ou, à défaut, celle de son unité légale) y est rangée,
  par exemple 42.22Z de « Travaux publics, routes, réseaux » vers « Réseaux électriques et télécoms »,
  ou, selon le propriétaire, « Mairies, administrations » vers « Communes et intercommunalités » ;
- lieux sans personnel (domaines.SANS_PERSONNEL) : comptes de collectivités et fermes solaires
  retirés de la catégorie ;
- codes retirés (domaines.CODES_RETIRES) : un établissement qui n'était dans la catégorie que par
  ce code en sort (62.02A, conseil en systèmes et logiciels).
Les badges La bonne alternance suivent l'établissement. Les formations viennent du code
(stage_donnees.catalogue_formations), qui relie déjà les nouvelles catégories.

Codes Insee de chaque établissement : CSV siret,naf,naf_u,cj (activité de l'établissement,
activité et catégorie juridique de l'unité légale), tirés des stocks Sirene, par exemple avec DuckDB :
  SELECT e.siret, e.activitePrincipaleEtablissement naf, u.activitePrincipaleUniteLegale naf_u,
         u.categorieJuridiqueUniteLegale cj
  FROM read_parquet('<stock-etablissement>') e JOIN read_parquet('<stock-unite-legale>') u USING (siren)
  WHERE e.siret IN (SIRET des fichiers concernés)

python3 source/stage_reclasser_naf.py --root /copie/carte-stages-donnees --naf insee.csv [--rapport reclassement-naf-lot.json] [--write]
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time

from domaines import CODES_RETIRES, DECOUPAGES, DOMAINES, SANS_PERSONNEL
from stage_collecte import atomic_json
from stage_donnees import affiner, catalogue_formations, fichier, sans_personnel, slug
from stage_catalogues import ecrire_catalogues


def lire(path):
    return json.loads(Path(path).read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--naf', type=Path, required=True, help='CSV siret,naf,naf_u,cj')
    p.add_argument('--rapport', default='reclassement-naf.json', help='Journal écrit à la racine des données (un par lot)')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.write and subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() in ('main', 'master', ''):
        p.error('Écriture réservée à une branche de travail')
    insee = {r['siret']: r for r in csv.DictReader(args.naf.open())}
    sec_of = {}
    for secs in DOMAINES.values():
        for s, codes in secs.items():
            for c in codes:
                sec_of.setdefault(c, slug(s))
    catalog = lire(root/'catalogue.json')
    presentes = {s['k'] for d in catalog['domaines'] for s in d['s']}
    # Seulement les découpages pas encore appliqués (les écoles le sont depuis la PR 41).
    enfants = {slug(e): slug(o) for e, o in DECOUPAGES.items() if slug(e) not in presentes}
    origines = set(enfants.values()) | {slug(s) for s in SANS_PERSONNEL} | {slug(s) for s in CODES_RETIRES}
    rangs, journal = {}, []
    bilan = dict(deplaces={}, retires={}, sans_code_insee=0)
    for dep in sorted(catalog['departements']):
        secteurs = catalog['departements'][dep]['secteurs']
        for k in sorted(origines & set(secteurs)):
            rows = lire(root/'sirene'/dep/(k+'.json'))
            reste = []
            for r in rows:
                i = insee.get(r[7])
                if not i or not i['naf']:
                    bilan['sans_code_insee'] += 1
                    reste.append(r)
                    continue
                if sans_personnel(k, i['naf'], i['cj'], i['naf_u']):
                    cle = f"{k} {i['naf']} {'public' if (i['cj'] or '').startswith('7') else 'agricole'}"
                    bilan['retires'][cle] = bilan['retires'].get(cle, 0) + 1
                    journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=None,
                                        naf=i['naf'], naf_unite_legale=i['naf_u'], categorie_juridique=i['cj']))
                    continue
                cible = sec_of.get(i['naf']) or sec_of.get(i['naf_u'])
                # Catégories sans code propre (communes) : même règle qu'à la collecte.
                if affiner(k, i['naf'], i['cj']) in enfants:
                    cible = affiner(k, i['naf'], i['cj'])
                if cible is None and any(slug(n) == k and i['naf'] in c for n, c in CODES_RETIRES.items()):
                    cle = f"{k} {i['naf']} code retiré"
                    bilan['retires'][cle] = bilan['retires'].get(cle, 0) + 1
                    journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=None,
                                        naf=i['naf'], naf_unite_legale=i['naf_u'], categorie_juridique=i['cj']))
                    continue
                if cible in enfants and enfants[cible] == k:
                    rangs.setdefault((dep, cible), []).append(r)
                    bilan['deplaces'][f'{k} -> {cible}'] = bilan['deplaces'].get(f'{k} -> {cible}', 0) + 1
                    journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=cible,
                                        naf=i['naf'], naf_unite_legale=i['naf_u'], categorie_juridique=i['cj']))
                    continue
                reste.append(r)
            rangs[(dep, k)] = reste
    print(json.dumps(bilan, ensure_ascii=False, indent=1))
    if not args.write:
        return
    for (dep, k), rows in rangs.items():
        path = root/'sirene'/dep/(k+'.json')
        rows = sorted(rows)
        if rows or k in catalog['departements'][dep]['secteurs']:
            catalog['departements'][dep]['secteurs'][k] = fichier(path, rows)
    # Badges La bonne alternance : suivent l'établissement, disparaissent avec lui.
    meta = lire(root/'lba/meta.json')
    for dep in sorted({j['dep'] for j in journal}):
        for k in sorted({j['de'] for j in journal if j['dep'] == dep}):
            src = root/'lba'/dep/(k+'.json')
            if not src.exists():
                continue
            d = lire(src)
            moves = {}
            for j in journal:
                if j['dep'] == dep and j['de'] == k and j['siret'] in d:
                    e = d.pop(j['siret'])
                    if j['vers']:
                        moves.setdefault(j['vers'], {})[j['siret']] = e
            atomic_json(src, d)
            for cible, entrees in moves.items():
                dst = root/'lba'/dep/(cible+'.json')
                atomic_json(dst, {**(lire(dst) if dst.exists() else {}), **entrees})
                if cible not in meta['files'].get(dep, []):
                    meta['files'][dep] = sorted(meta['files'].get(dep, []) + [cible])
    atomic_json(root/'lba/meta.json', meta)
    code = catalogue_formations()
    catalog['domaines'] = [dict(d, s=[dict(s, c=sum(x['secteurs'][s['k']]['n'] for x in catalog['departements'].values()
                                                       if s['k'] in x['secteurs'])) for s in d['s']]) for d in code['domaines']]
    catalog['formations'] = code['formations']
    catalog['version'] = hashlib.sha256(json.dumps(catalog['departements'], sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json', catalog)
    ecrire_catalogues(root)
    deps = {dep for dep, _ in rangs}
    b = lire(root/'bilan.json')
    for e in b['departements']:
        if e['dep'] in deps:
            files = catalog['departements'][e['dep']]['secteurs']
            e['lignes'] = sum(v['n'] for v in files.values())
            e['bytes'] = sum(v['bytes'] for v in files.values()) + catalog['departements'][e['dep']]['lycees']['bytes']
    atomic_json(root/'bilan.json', b)
    sizepath = root/'tailles-fichiers.csv'
    with sizepath.open(newline='') as f:
        rows = {r['fichier']: r for r in csv.DictReader(f)}
    for dep, k in rangs:
        name = f'sirene/{dep}/{k}.json'
        path = root/name
        if path.exists():
            rows[name] = dict(fichier=name, octets=path.stat().st_size, lignes=len(lire(path)))
    with sizepath.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fichier', 'octets', 'lignes'], lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r['fichier']))
    atomic_json(root/args.rapport, dict(
        date=time.strftime('%Y-%m-%d'),
        regle=dict(decoupages={e: o for e, o in DECOUPAGES.items() if slug(e) in enfants}, sans_personnel=SANS_PERSONNEL,
                   codes_retires=CODES_RETIRES),
        bilan=bilan, details=journal))


if __name__ == '__main__':
    main()
