"""Contrôles des sorties nationales et des invariants de confidentialité."""
import collections
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
CAT=json.loads((ROOT/'commun/academies.json').read_text())
assert len(CAT)==30 and len({a['slug'] for a in CAT})==30
assert all(set(a)=={'slug','nom','deps','region'} for a in CAT)
departments=[d for a in CAT for d in a['deps']]
assert len(departments)==101 and len(set(departments))==101
assert all(re.fullmatch(r'[a-z]+(?:-[a-z]+)*',a['slug']) for a in CAT)
assert (ROOT/'aide/aide.json').read_bytes()==subprocess.check_output(['git','show','origin/main:aide/aide.json'],cwd=ROOT)
email=re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
types={'cio','ml','ij','bib','mda'}
allowed={'t','n','a','cp','v','dep','ac','lat','lon','tel','w','h','sp','maj','pl','po','wifi','dim','src','pub'}
total=collections.Counter()
for a in CAT:
 p=ROOT/'aide/data'/f"{a['slug']}.json";data=json.loads(p.read_text());name=re.sub(r"^Académie (?:de |d')",'',a['nom'])
 assert p.stat().st_size<500_000,p
 assert data['lieux'] and data['colleges'],p
 assert (ROOT/'aide'/a['slug']/'index.html').exists()
 assert not email.search(p.read_text()),p
 for r in data['lieux']:
  assert set(r)<=allowed and r['t'] in types
  assert r['ac']==name
  assert math.isfinite(r['lat']) and math.isfinite(r['lon'])
  assert -90<=r['lat']<=90 and -180<=r['lon']<=180
  assert not r['tel'] or re.fullmatch(r'(?:0\d(?: \d{2}){4}|\+\d{10,14})',r['tel']),r
  assert not r.get('w') or r['w'].startswith(('http://','https://'))
  if r['t']=='mda':assert r['src'].startswith('https://anmda.fr/fr/')
  total[r['t']]+=1
 for c in data['colleges']:assert c['ac']==name and all(k in c for k in ['n','v','lat','lon'])
assert not email.search((ROOT/'aide/data/mda-france.json').read_text())
spec=importlib.util.spec_from_file_location('aide',ROOT/'source/aide.py');aide=importlib.util.module_from_spec(spec);spec.loader.exec_module(aide)
assert aide.telephone('02 98 10 20 35 OU 06 22 32 07 76')=='02 98 10 20 35'
assert aide.telephone('0544000221 - 06 10 89 60 33')=='05 44 00 02 21'
assert aide.telephone('tel inconnu')==''
print('30 académies, 101 départements, schémas, téléphones, courriels, tailles et conservation IDF : OK')
print('Lieux :',dict(total))
