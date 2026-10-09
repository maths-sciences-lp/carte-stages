"""Retire de la carte les entreprises en liquidation judiciaire (annonces du BODACC).

Le stock Sirene laisse une entreprise « active » jusqu'à sa radiation, parfois des mois
après le jugement. Les procédures collectives publiées au BODACC (open data DILA, depuis le
1er janvier 2023) disent où en est chaque entreprise. Pour chaque SIREN, on garde la
décision la plus récente parmi :
- liquidation : ouverture ou conversion en liquidation judiciaire, résolution d'un plan avec
  liquidation, extension ou reprise de liquidation, clôture pour insuffisance d'actif ;
- poursuite : ouverture d'un redressement ou d'une sauvegarde, plan de redressement, de
  sauvegarde ou de continuation, fin du redressement, clôture pour extinction du passif,
  rétractation, arrêt d'appel infirmant.
Si c'est une liquidation, tous les établissements de l'entreprise quittent la carte. Un
redressement seul ne retire rien : l'entreprise continue de travailler. Les avis
rectificatifs et d'annulation sont ignorés ; les dépôts de créances ne décident rien.
Journal : liquidations-bodacc.json (SIRET, nom, jugement, date, numéro d'annonce).

python3 source/stage_bodacc.py --root /copie/carte-stages-donnees --cache ~/.cache/bodacc [--write]
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.parse

from stage_collecte import atomic_json
from stage_donnees import fichier
from stage_catalogues import ecrire_catalogues

API = 'https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/exports/csv?'
LIQ = re.compile(r"ouverture de liquidation judiciaire|conversion en liquidation judiciaire|et la liquidation judiciaire"
                 r"|extension de liquidation judiciaire|reprise de la procédure de liquidation judiciaire"
                 r"|clôture pour insuffisance d'actif", re.I)
VIE = re.compile(r"plan de redressement|plan de sauvegarde|plan de continuation|mettant fin à la procédure de redressement"
                 r"|extinction du passif|Rétractation|infirmant|ouverture d'une procédure de redressement"
                 r"|ouverture d'une procédure de sauvegarde|conversion en redressement", re.I)


def lire(path):
    return json.loads(Path(path).read_text())


def telecharger(cache):
    """Export CSV des procédures collectives depuis 2023 (environ 380 Mo), gardé un jour."""
    path = cache/'collectives.csv'
    if not path.exists() or time.time() - path.stat().st_mtime > 86400:
        cache.mkdir(parents=True, exist_ok=True)
        q = dict(select='id,registre,dateparution,typeavis,jugement', delimiter=';',
                 where='familleavis="collective" and dateparution>="2023-01-01"')
        part = path.with_suffix('.part')
        subprocess.run(['curl', '-fsSL', '--max-time', '1800', '--retry', '3', '-o', str(part),
                        API + urllib.parse.urlencode(q)], check=True)
        if part.stat().st_size < 10_000_000:
            raise ValueError('Export BODACC inattendu ou incomplet')
        part.replace(path)
    return path


def liquidees(path):
    csv.field_size_limit(10**9)
    ev = collections.defaultdict(list)
    with path.open(encoding='utf-8-sig') as f:
        for r in csv.DictReader(f, delimiter=';'):
            if r['typeavis'] != 'annonce':
                continue
            try:
                j = json.loads(r['jugement'] or '{}')
            except ValueError:
                continue
            nature = j.get('nature') or ''
            sorte = 'liq' if LIQ.search(nature) else 'vie' if VIE.search(nature) else None
            m = re.search(r'\d{9}', (r['registre'] or '').replace(' ', ''))
            if sorte and m:
                ev[m.group(0)].append(((j.get('date') or r['dateparution'])[:10], r['dateparution'], sorte, nature, r['id']))
    out = {}
    for siren, events in ev.items():
        events.sort()
        if events[-1][2] == 'liq':
            out[siren] = dict(date=events[-1][0], jugement=events[-1][3], annonce=events[-1][4])
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--cache', type=Path, default=Path.home()/'.cache'/'bodacc')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.write and subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() in ('main', 'master', ''):
        p.error('Écriture réservée à une branche de travail')
    liq = liquidees(telecharger(args.cache))
    catalog = lire(root/'catalogue.json')
    gardes, journal = {}, []
    for dep in sorted(catalog['departements']):
        for k in sorted(catalog['departements'][dep]['secteurs']):
            rows = lire(root/'sirene'/dep/(k+'.json'))
            reste = [r for r in rows if r[7][:9] not in liq]
            if len(reste) != len(rows):
                gardes[(dep, k)] = reste
                journal += [dict(dep=dep, secteur=k, siret=r[7], nom=r[0], enseigne=r[1], **liq[r[7][:9]])
                            for r in rows if r[7][:9] in liq]
    bilan = dict(entreprises_liquidees_bodacc=len(liq), lignes_retirees=len(journal),
                 etablissements_retires=len({j['siret'] for j in journal}),
                 par_jugement=dict(collections.Counter(j['jugement'] for j in journal).most_common()))
    print(json.dumps(bilan, ensure_ascii=False, indent=1))
    if not args.write:
        return
    for (dep, k), rows in gardes.items():
        catalog['departements'][dep]['secteurs'][k] = fichier(root/'sirene'/dep/(k+'.json'), rows)
    for dep, k in sorted(gardes):
        src = root/'lba'/dep/(k+'.json')
        if src.exists():
            d = lire(src)
            n = len(d)
            d = {s: e for s, e in d.items() if s[:9] not in liq}
            if len(d) != n:
                atomic_json(src, d)
    for d in catalog['domaines']:
        for s in d['s']:
            s['c'] = sum(x['secteurs'][s['k']]['n'] for x in catalog['departements'].values() if s['k'] in x['secteurs'])
    catalog['version'] = hashlib.sha256(json.dumps(catalog['departements'], sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json', catalog)
    ecrire_catalogues(root)
    deps = {dep for dep, _ in gardes}
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
    for dep, k in gardes:
        name = f'sirene/{dep}/{k}.json'
        rows[name] = dict(fichier=name, octets=(root/name).stat().st_size, lignes=len(gardes[(dep, k)]))
    with sizepath.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fichier', 'octets', 'lignes'], lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r['fichier']))
    atomic_json(root/'liquidations-bodacc.json', dict(
        date=time.strftime('%Y-%m-%d'), source='BODACC, annonces commerciales, procédures collectives depuis le 1er janvier 2023',
        bilan=bilan, details=journal))


if __name__ == '__main__':
    main()
