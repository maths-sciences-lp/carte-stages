"""Reclasse les établissements publiés qui ne passent pas les filtres de noms (domaines.FILTRES).

Cas d'octobre 2026 : bains-douches municipaux rangés dans « Esthétique, soins de beauté »
(code 96.04Z, entretien corporel). Comme à la collecte (stage_donnees.preparer), un
établissement refusé par le filtre est rangé selon l'activité de son unité légale
(ex. commune → « Mairies, administrations ») ; si elle ne correspond à aucun type, il
est retiré. Les badges La bonne alternance suivent l'établissement.

python3 source/stage_reclasser.py --root /copie/carte-stages-donnees [--write]
Sans --write : bilan seulement. Écriture réservée à une copie sur une branche de travail.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.request

from domaines import DOMAINES, FILTRES
from stage_collecte import atomic_json
from stage_donnees import fichier, slug
from stage_catalogues import ecrire_catalogues

API = 'https://recherche-entreprises.api.gouv.fr/search?q='


def lire(path):
    return json.loads(Path(path).read_text())


def naf(siret, memo):
    """(activité de l'établissement, activité de l'unité légale), mêmes champs que la collecte."""
    if siret not in memo:
        req = urllib.request.Request(API + siret, headers={'User-Agent': 'carte-stages (maths-sciences-pro.fr)'})
        for essai in range(4):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    res = json.load(r)['results']
                u = res[0] if res and res[0]['siren'] == siret[:9] else None
                e = next((m for m in (u or {}).get('matching_etablissements', []) if m['siret'] == siret), None)
                memo[siret] = [e.get('activite_principale') if e else None, u.get('activite_principale') if u else None]
                break
            except Exception:
                time.sleep(2 * (essai + 1))
        else:
            raise RuntimeError('API Recherche d’entreprises indisponible pour ' + siret)
        time.sleep(0.25)
    return memo[siret]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.write:
        branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip()
        if branch in ('main', 'master', ''):
            p.error('Écriture réservée à une branche de travail')
    sec_of = {}
    for secs in DOMAINES.values():
        for s, codes in secs.items():
            for c in codes:
                sec_of.setdefault(c, slug(s))
    filtres = {slug(k): re.compile(v) for k, v in FILTRES.items()}
    catalog = lire(root/'catalogue.json')
    memo_path = Path.home()/'.cache'/'carte-stages-reclassement-naf.json'
    memo = lire(memo_path) if memo_path.exists() else {}
    journal, touches, lba_moves = [], {}, []
    for dep, details in sorted(catalog['departements'].items()):
        for k in sorted(set(details['secteurs']) & set(filtres)):
            path = root/'sirene'/dep/(k+'.json')
            rows = lire(path)
            refus = [r for r in rows if not filtres[k].search((r[0] + ' ' + (r[1] or '')).upper())]
            if not refus:
                continue
            touches.setdefault((dep, k), list(rows))
            for r in refus:
                c, q = naf(r[7], memo)
                # Même règle qu'à la collecte : refusé par le filtre, l'établissement est rangé
                # selon l'activité de son unité légale si elle diffère de la sienne, sinon retiré.
                cible = sec_of.get(q) if q and q != c else None
                if cible == k:
                    continue
                if cible and cible not in details['secteurs']:
                    cible = None
                journal.append(dict(dep=dep, siret=r[7], nom=r[0], enseigne=r[1], adresse=r[2], de=k, naf_etablissement=c, naf_unite_legale=q, vers=cible))
                touches[(dep, k)] = [x for x in touches[(dep, k)] if x[7] != r[7]]
                if cible:
                    dest = touches.setdefault((dep, cible), lire(root/'sirene'/dep/(cible+'.json')))
                    if r[7] not in {x[7] for x in dest}:
                        dest.append(r)
                lba_moves.append((dep, k, cible, r[7]))
    atomic_json(memo_path, memo)
    bilan = dict(reclasses=sum(1 for j in journal if j['vers']), retires=sum(1 for j in journal if not j['vers']),
                 par_cible={c: sum(1 for j in journal if j['vers'] == c) for c in sorted({j['vers'] or '' for j in journal})})
    print(json.dumps(bilan, ensure_ascii=False))
    if not args.write:
        return
    for (dep, k), rows in touches.items():
        path = root/'sirene'/dep/(k+'.json')
        atomic_json(path, rows)
        catalog['departements'][dep]['secteurs'][k] = fichier(path, rows)
    # Badges La bonne alternance : suivent l'établissement.
    meta = lire(root/'lba/meta.json')
    for dep, k, cible, siret in lba_moves:
        src = root/'lba'/dep/(k+'.json')
        if not src.exists():
            continue
        d = lire(src)
        if siret not in d:
            continue
        entree = d.pop(siret)
        atomic_json(src, d)
        if cible:
            dst = root/'lba'/dep/(cible+'.json')
            dd = lire(dst) if dst.exists() else {}
            dd[siret] = entree
            atomic_json(dst, dd)
            if cible not in meta['files'].setdefault(dep, []):
                meta['files'][dep] = sorted(meta['files'][dep] + [cible])
    atomic_json(root/'lba/meta.json', meta)
    for domain in catalog['domaines']:
        for sec in domain['s']:
            sec['c'] = sum(d['secteurs'][sec['k']]['n'] for d in catalog['departements'].values() if sec['k'] in d['secteurs'])
    catalog['version'] = hashlib.sha256(json.dumps(catalog['departements'], sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json', catalog)
    ecrire_catalogues(root)
    deps = sorted({dep for dep, _ in touches})
    bilan_global = lire(root/'bilan.json')
    for entry in bilan_global['departements']:
        if entry['dep'] not in deps:
            continue
        files = catalog['departements'][entry['dep']]['secteurs']
        entry['apres_classement'] = len({r[7] for k in files for r in lire(root/'sirene'/entry['dep']/(k+'.json'))})
        entry['lignes'] = sum(v['n'] for v in files.values())
        entry['bytes'] = sum(v['bytes'] for v in files.values()) + catalog['departements'][entry['dep']]['lycees']['bytes']
    atomic_json(root/'bilan.json', bilan_global)
    sizepath = root/'tailles-fichiers.csv'
    with sizepath.open(newline='') as f:
        sizerows = list(csv.DictReader(f))
    touched = {f'sirene/{dep}/{k}.json' for dep, k in touches}
    for r in sizerows:
        if r['fichier'] in touched:
            path = root/r['fichier']
            r['octets'] = path.stat().st_size
            r['lignes'] = len(lire(path))
    with sizepath.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fichier', 'octets', 'lignes'], lineterminator='\n')
        w.writeheader()
        w.writerows(sizerows)
    atomic_json(root/'reclassement-filtres-noms.json', dict(date=time.strftime('%Y-%m-%d'), regle=FILTRES, bilan=bilan, details=journal))


if __name__ == '__main__':
    main()
