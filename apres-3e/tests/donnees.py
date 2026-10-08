"""Invariants des données publiables : périmètre, sources, chiffres et vie privée.
Option --sources : vérifie aussi chaque offre contre le CSV Onisep d'origine.
"""
import argparse
import collections
import csv
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'source'))
from apres3e import nom, T
from domaines_apres3e import DOM, domaines
from corrections_apres3e import C

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sources',type=Path)
args=parser.parse_args()
catalog=json.loads((ROOT/'commun/academies.json').read_text())
bilan=json.loads((ROOT/'apres-3e/data/bilan.json').read_text())
source={}
if args.sources:
    with (args.sources/'605340ddc19a9.csv').open(encoding='utf-8-sig') as f:
        for r in csv.DictReader(f,delimiter=';'):
            if r['FOR type'] in T:
                source.setdefault((r['ENS académie'],nom(r['Formation (FOR) libellé']),r['ENS URL et ID Onisep']),[]).append(r)
total=collections.Counter()
for ac in catalog:
    p=ROOT/'apres-3e/data'/f"{ac['slug']}.json"
    data=json.loads(p.read_text())
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',p.read_text()),p
    assert p.stat().st_size < 1_000_000,p
    assert (ROOT/'apres-3e'/ac['slug']/'index.html').exists()
    assert data['colleges'] and data['formations']
    assert data['domaines']==[dict(k=k,i=i,n=n,s=s) for k,i,n,s,_,_ in DOM]
    name=re.sub(r"^Académie (?:de |d')",'',ac['nom'])
    for c in data['colleges']:
        assert set(c)=={'n','v','lat','lon'}
        assert math.isfinite(c['lat']) and math.isfinite(c['lon'])
    for f in data['formations']:
        assert f['e'] and f['t'] in {'CAP','Bac pro','2de pro'}
        assert set(f['d'])<={d['k'] for d in data['domaines']}
        for e in f['e']:
            assert set(e)<={'n','st','a','cp','v','dep','ac','lat','lon','w','o','h','af','c','ij','it','ic','p','du'}
            assert e.get('du',f['du']) and e.get('du')!=f['du']
            assert e['ac']==name
            assert -90<=e['lat']<=90 and -180<=e['lon']<=180
            assert e['v']!='Monaco'
            assert 'p' not in e or ac['slug']=='creteil'
            assert not e['ij'] or all(v is None or 0<=v<=100 for v in e['ij'].values())
            assert e.get('it') in {None,'i','a','v'}
            if e.get('it')=='a':assert 'hors établissement' in e['h'] or 'internat délocalisé' in e['h']
            if source:
                candidates=source[(name,f['n'],e['o'])]
                assert any(e['n']==r["Lieu d'enseignement (ENS) libellé"] and e['a']==r['ENS adresse'] and e['cp']==r['ENS code postal'] and e['h']==r['ENS hébergement'] for r in candidates)
                # Durée du lycée : toutes les durées Onisep de cette offre, rien d'autre.
                durees={r['AF durée cycle standard'] for r in candidates if r["Lieu d'enseignement (ENS) libellé"]==e['n']}
                assert e.get('du',f['du'])==' ou '.join(sorted(durees)),(e['n'],f['n'],e.get('du',f['du']),durees)
                assert any(f['d']==(C[r['Formation (FOR) libellé']].split(',') if r['Formation (FOR) libellé'] in C else domaines(r['Formation (FOR) libellé'],r['FOR indexation domaine web Onisep'])) for r in candidates)
    stats=next(r for r in bilan['academies'] if r['slug']==ac['slug'])
    assert stats['octets']==p.stat().st_size
    assert stats['formations']==len(data['formations'])
    assert stats['colleges']==len(data['colleges'])
    assert stats['offres']==sum(len(f['e']) for f in data['formations'])
    total.update({k:stats[k] for k in ['offres','lycees','colleges']})
for name in ['aide/aide.json','apres-3e/apres3e.json','formation/formations.json']:
    assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','origin/main:'+name],cwd=ROOT)
assert not subprocess.check_output(['git','diff','origin/main','--','commun'],cwd=ROOT)
print('30 académies : données, domaines, coordonnées, internats, pression Créteil seule, tailles et absence de courriels OK')
if source:print('Chaque offre : formation, établissement, adresse, hébergement et domaines conformes au CSV Onisep')
print('Module commun et trois JSON historiques : inchangés')
print(dict(total))
