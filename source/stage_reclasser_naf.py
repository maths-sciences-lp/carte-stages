"""Applique aux données publiées les découpages et les lieux sans personnel de domaines.py.

Mêmes règles que stage_donnees.preparer, sans refaire la collecte :
- découpage (domaines.DECOUPAGES) : un établissement d'une catégorie d'origine passe dans la
  nouvelle catégorie quand son activité (ou, à défaut, celle de son unité légale) y est rangée,
  par exemple 42.22Z de « Travaux publics, routes, réseaux » vers « Réseaux électriques et télécoms »,
  ou, selon le propriétaire, « Mairies, administrations » vers « Communes et intercommunalités » ;
- lieux sans personnel (domaines.SANS_PERSONNEL) : comptes de collectivités et fermes solaires
  retirés de la catégorie ;
- catégorie remplacée (absente de DOMAINES, présente dans DECOUPAGES) : ses établissements vont
  dans les nouvelles catégories par leur code ou leur nom (MOTS_CLES), puis ses fichiers disparaissent ;
- catégories remplies par le nom seul (ex. enseignes) : la règle de nom actuelle est réappliquée ;
- codes retirés (domaines.CODES_RETIRES) : un établissement qui n'était dans la catégorie que par
  ce code en sort (62.02A, conseil en systèmes et logiciels) ;
- sources des règles de nom resserrées (domaines.MOTS_CLES_SOURCES) : un établissement venu par
  son nom d'une catégorie qui n'est plus permise en sort ;
- types copiés (domaines.COPIES) : refaits depuis leur type d'origine (hôpitaux avec service
  technique, bailleurs sociaux).
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
import re
import subprocess
import time

from domaines import CODES_RETIRES, COPIES, DECOUPAGES, DOMAINES, FILTRES, MOTS_CLES, MOTS_CLES_SOURCES, SANS_PERSONNEL
from stage_collecte import atomic_json
from stage_donnees import affiner, catalogue_formations, copie, fichier, sans_personnel, slug
from stage_catalogues import ecrire_catalogues


def lire(path):
    return json.loads(Path(path).read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--naf', type=Path, required=True, help='CSV siret,naf,naf_u,cj')
    p.add_argument('--rapport', default='reclassement-naf.json', help='Journal écrit à la racine des données (un par lot)')
    p.add_argument('--filtres', nargs='*', help='types dont le filtre de nom (domaines.FILTRES) est réappliqué')
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
    # Catégorie remplacée (absente de DOMAINES) : chaque établissement va dans la nouvelle
    # catégorie de son code, et aussi dans celles dont le nom correspond (MOTS_CLES), comme
    # à la collecte ; sinon il reste seulement dans sa catégorie d'origine. Ex. 2026-10 :
    # « Menuiserie, agencement, serrurerie » → bois / métallique.
    actuelles = {slug(s) for ss in DOMAINES.values() for s in ss}
    remplacees = {o for o in enfants.values() if o not in actuelles}
    mots = {slug(n): re.compile(rx) for n, rx in MOTS_CLES.items()}
    # Catégories remplies seulement par le nom (aucun code) : on réapplique leur règle de nom.
    mots_seuls = {slug(n) for d in DOMAINES.values() for n, c in d.items() if not c and slug(n) in mots}
    origines |= mots_seuls
    # Règles de nom aux sources resserrées : un établissement entré seulement par son nom depuis
    # une catégorie qui n'est plus permise en sort (son code le range ailleurs).
    permises = {slug(n): {slug(s) for s in ss} for n, ss in MOTS_CLES_SOURCES.items()}
    origines |= set(permises)
    # Filtres de nom (domaines.FILTRES) réappliqués aux données publiées, seulement pour les types
    # nommés par --filtres : un établissement dont le nom ne passe plus le filtre de son type en sort.
    filtres = {slug(n): re.compile(rx) for n, rx in FILTRES.items() if n in (args.filtres or [])}
    origines |= set(filtres)
    for dep in sorted(catalog['departements']):
        secteurs = catalog['departements'][dep]['secteurs']
        for k in sorted(remplacees & set(secteurs)):
            for r in lire(root/'sirene'/dep/(k+'.json')):
                i = insee.get(r[7]) or {}
                fils = [e for e, o in enfants.items() if o == k]
                cibles = {c for c in (sec_of.get(i.get('naf')) or sec_of.get(i.get('naf_u')),) if c in fils}
                texte = (r[0] + ' ' + (r[1] or '')).upper()
                cibles |= {e for e in fils if e in mots and mots[e].search(texte) and 'ENSEIGNEMENT' not in texte}
                for cible in sorted(cibles) or [None]:
                    if cible:
                        rangs.setdefault((dep, cible), []).append(r)
                    cle = f'{k} -> {cible or "hors de ses nouvelles catégories"}'
                    bilan['deplaces'][cle] = bilan['deplaces'].get(cle, 0) + 1
                    journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=cible,
                                        naf=i.get('naf'), naf_unite_legale=i.get('naf_u'), categorie_juridique=i.get('cj')))
        for k in sorted((origines - remplacees) & set(secteurs)):
            rows = lire(root/'sirene'/dep/(k+'.json'))
            reste = []
            for r in rows:
                if k in mots_seuls:
                    texte = (r[0] + ' ' + (r[1] or '')).upper()
                    if mots[k].search(texte) and 'ENSEIGNEMENT' not in texte:
                        reste.append(r)
                    else:
                        cle = f'{k} : nom hors de la règle'
                        bilan['retires'][cle] = bilan['retires'].get(cle, 0) + 1
                        journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=None))
                    continue
                if k in filtres and not filtres[k].search((r[0] + ' ' + (r[1] or '')).upper()):
                    cle = f'{k} : nom hors du filtre'
                    bilan['retires'][cle] = bilan['retires'].get(cle, 0) + 1
                    journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=None))
                    continue
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
                fin = affiner(k, i['naf'], i['cj'], r[7], r[0] + ' ' + (r[1] or ''))
                if fin in enfants:
                    cible = fin
                if k in permises and cible not in (None, k) and cible not in permises[k] and cible not in enfants:
                    cle = f'{k} : nom venu de {cible}'
                    bilan['retires'][cle] = bilan['retires'].get(cle, 0) + 1
                    journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], de=k, vers=None,
                                        naf=i['naf'], naf_unite_legale=i['naf_u'], categorie_juridique=i['cj']))
                    continue
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
    # Types copiés (domaines.COPIES) : recalculés en entier depuis leur type d'origine.
    copies = {}
    for dep in sorted(catalog['departements']):
        secteurs = catalog['departements'][dep]['secteurs']
        for cible, regle in COPIES.items():
            src, k = slug(regle['source']), slug(cible)
            if src not in secteurs and (dep, src) not in rangs:
                continue
            gardes = [r for r in rangs.get((dep, src)) or lire(root/'sirene'/dep/(src+'.json'))
                      if (i := insee.get(r[7])) and copie(regle, i['naf'], i['cj'], r[0], r[1])]
            if gardes or k in secteurs:
                rangs[(dep, k)] = gardes
                copies[(dep, k)] = (src, {r[7] for r in gardes})
                bilan.setdefault('copies', {})[k] = bilan.get('copies', {}).get(k, 0) + len(gardes)
    print(json.dumps(bilan, ensure_ascii=False, indent=1))
    if not args.write:
        return
    for (dep, k), rows in rangs.items():
        path = root/'sirene'/dep/(k+'.json')
        rows = sorted(rows)
        if rows or k in catalog['departements'][dep]['secteurs']:
            catalog['departements'][dep]['secteurs'][k] = fichier(path, rows)
    for dep, details in catalog['departements'].items():
        for k in remplacees & set(details['secteurs']):
            del details['secteurs'][k]
            (root/'sirene'/dep/(k+'.json')).unlink()
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
                if j['dep'] == dep and j['de'] == k and j['siret'] in d and j['vers']:
                    moves.setdefault(j['vers'], {})[j['siret']] = d[j['siret']]
            for j in journal:
                if j['dep'] == dep and j['de'] == k:
                    d.pop(j['siret'], None)
            if k in remplacees:
                src.unlink()
                meta['files'][dep] = [f for f in meta['files'].get(dep, []) if f != k]
            else:
                atomic_json(src, d)
            for cible, entrees in moves.items():
                dst = root/'lba'/dep/(cible+'.json')
                atomic_json(dst, {**(lire(dst) if dst.exists() else {}), **entrees})
                if cible not in meta['files'].get(dep, []):
                    meta['files'][dep] = sorted(meta['files'].get(dep, []) + [cible])
    for (dep, k), (src, sirets) in copies.items():
        source = root/'lba'/dep/(src+'.json')
        entrees = {s: e for s, e in lire(source).items() if s in sirets} if source.exists() else {}
        if entrees or (root/'lba'/dep/(k+'.json')).exists():
            atomic_json(root/'lba'/dep/(k+'.json'), entrees)
            if k not in meta['files'].get(dep, []):
                meta['files'][dep] = sorted(meta['files'].get(dep, []) + [k])
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
    rows = {n: r for n, r in rows.items() if (root/n).exists()}
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
