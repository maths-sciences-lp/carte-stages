"""Complément Onisep, sans retirer ni déplacer les établissements existants.

Usage : stage_lycees.py --root /copie/donnees --onisep 605340ddc19a9.csv
Les contacts sont ignorés. Les exceptions restent dans un rapport public.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import unicodedata
from stage_collecte import atomic_json
from stage_catalogues import ecrire_catalogues

TYPES={'CAP','CAP agricole','baccalauréat professionnel','classe de 2de professionnelle',"brevet des métiers d'art"}
# Deux sites Onisep pour cet UAI : le point Plabennec est confirmé par l'annuaire.
SITES_VERIFIES={'0291604L':'Plabennec'}

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if c.isalnum())

def completer(root, onisep):
    root,onisep=Path(root),Path(onisep)
    cat=json.loads((root/'catalogue.json').read_text())
    schools={d:json.loads((root/'lycees'/f'{d}.json').read_text()) for d in cat['departements']}
    existing={r['u'] for rows in schools.values() for r in rows}
    previous=root/'rapport-lycees-onisep.json'
    if previous.exists():
        saved=json.loads(previous.read_text())
        if saved.get('source_sha256')==hashlib.sha256(onisep.read_bytes()).hexdigest() and all(x['uai'] in existing for x in saved['ajouts']):
            actualiser_bilan(root, cat)
            ecrire_catalogues(root)
            return saved
    deps={norm(v['nom']):d for d,v in cat['departements'].items()}
    groups=defaultdict(list);no_uai=[]
    for r in csv.DictReader(onisep.open(encoding='utf-8-sig'),delimiter=';'):
        if r['FOR type'] not in TYPES:continue
        if not r['ENS code UAI']:
            no_uai.append(r['ENS URL et ID Onisep']);continue
        if r['ENS code UAI'] not in existing:groups[r['ENS code UAI']].append(r)
    report={'source':'https://opendata.onisep.fr/data/605340ddc19a9/','source_sha256':hashlib.sha256(onisep.read_bytes()).hexdigest(),
            'date_verification':'2026-10-08','avant':len(existing),'uai_absents':len(groups),'ajouts':[], 'exceptions':[],
            'lignes_sans_uai':len(no_uai),'fiches_sans_uai':sorted(set(no_uai))}
    for uai,rs in sorted(groups.items()):
        r=rs[0];dep=deps.get(norm(r['ENS département']))
        info={'uai':uai,'nom':r["Lieu d'enseignement (ENS) libellé"],'commune':r['ENS commune'],
              'sources':sorted({x['ENS URL et ID Onisep'] for x in rs})}
        if dep is None or r['ENS code postal'] in {'99999','98000'}:
            report['exceptions'].append(dict(info,raison='Hors des 30 académies couvertes'));continue
        sites={(x['ENS commune'],x['ENS latitude'],x['ENS longitude']) for x in rs}
        if len(sites)>1:
            if uai not in SITES_VERIFIES:
                report['exceptions'].append(dict(info,raison='Plusieurs implantations pour un UAI : point non tranché',sites=sorted(sites)));continue
            r=next(x for x in rs if x['ENS commune']==SITES_VERIFIES[uai])
            info['verification']='Annuaire Éducation nationale : UAI 0291604L, Plabennec (48.50573108250989, -4.430130088427793), consulté le 08/10/2026'
        lat,lon=float(r['ENS latitude']),float(r['ENS longitude'])
        if not -90<=lat<=90 or not -180<=lon<=180 or (lat,lon)==(0,0):raise ValueError('Coordonnées invalides : '+uai)
        row=dict(u=uai,n=r["Lieu d'enseignement (ENS) libellé"],c=r['ENS commune'],p=r['ENS code postal'],la=lat,lo=lon)
        schools[dep].append(row);report['ajouts'].append(dict(info,departement=dep,etablissement=row))
    for dep,rows in schools.items():
        path=root/'lycees'/f'{dep}.json'
        if len(rows)==cat['departements'][dep]['lycees']['n']:continue
        atomic_json(path,rows)
        raw=path.read_bytes();cat['departements'][dep]['lycees']={'n':len(rows),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    report['apres']=sum(map(len,schools.values()))
    cat['version']=hashlib.sha256(json.dumps(cat['departements'],sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json',cat)
    atomic_json(root/'rapport-lycees-onisep.json',report)
    actualiser_bilan(root, cat)
    ecrire_catalogues(root)
    return report

def actualiser_bilan(root, cat):
    p=root/'bilan.json'
    if not p.exists():return
    bilan=json.loads(p.read_text())
    for r in bilan['departements']:
        meta=cat['departements'][r['dep']]
        r['lycees']=meta['lycees']['n']
        r['bytes']=sum(x['bytes'] for x in meta['secteurs'].values())+meta['lycees']['bytes']
    bilan['complement_lycees']='rapport-lycees-onisep.json'
    atomic_json(p,bilan)
    by={r['dep']:r for r in bilan['departements']}
    with (root/'bilan-academies.csv').open('w',newline='') as stream:
        w=csv.writer(stream,lineterminator='\n');w.writerow(['academie','departements','etablissements','lycees','octets_sirene_et_lycees'])
        for ac in cat['academies']:
            rows=[by[d] for d in ac['deps']]
            w.writerow([ac['slug'],', '.join(ac['deps']),sum(r['apres_classement'] for r in rows),sum(r['lycees'] for r in rows),sum(r['bytes'] for r in rows)])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--onisep',type=Path,required=True)
    a=p.parse_args();r=completer(a.root,a.onisep)
    print(f"{r['avant']} → {r['apres']} UAI ; {len(r['ajouts'])} ajouts ; {len(r['exceptions'])} exceptions")
