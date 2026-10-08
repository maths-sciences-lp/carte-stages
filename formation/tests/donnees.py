"""Contrôles de provenance, périmètre régional et rapprochements. Sources hors dépôt."""
import argparse,csv,json,re,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'source'))
from apres_lycee import exemples,TYPES
from parcoursup import meme_bts,km,nom_proche,norm
p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);a=p.parse_args()
raw=[]
for name in ['sup2.csv','605340ddc19a9.csv']:
 raw+=list(csv.DictReader((a.sources/name).open(encoding='utf-8-sig'),delimiter=';'))
regions={};departures={}
for r in raw:
 regions.setdefault((r['FOR URL et ID Onisep'],r['ENS URL et ID Onisep']),set()).add(r['ENS région'].replace('Ile-de-France','Île-de-France'))
 if r['FOR type'] in TYPES:
  u=r['ENS code UAI'] or 'onisep:'+r['ENS URL et ID Onisep'].split('.')[-1]
  departures.setdefault((r['FOR URL et ID Onisep'].split('.')[-1],u),set()).add(r['ENS académie'])
psraw={int(re.search(r'g_ta_cod=(\d+)',r['lien_form_psup']).group(1)):r for r in json.loads((a.cache/'parcoursup-national.json').read_text()) if re.search(r'g_ta_cod=(\d+)',r['lien_form_psup'] or '')}
revues={r['onisep']+'|'+str(r['parcoursup']):r for r in json.loads((ROOT/'source/formation_parcoursup_revues.json').read_text())}
n=0
for ac in json.loads((ROOT/'commun/academies.json').read_text()):
 path=ROOT/'formation/data'/f"{ac['slug']}.json";d=json.loads(path.read_text());ps=json.loads(path.with_name(ac['slug']+'-parcoursup.json').read_text())
 assert d['region']==ac['region'] and d['academie']==ac['nom']
 assert (ROOT/'formation'/ac['slug']/'index.html').exists()
 assert bool(d['classes'])==(ac['slug']=='creteil')
 for fid,x in d['dip'].items():
  cites={t.lower() for t in exemples(fid,str(a.cache/'fiches'))}
  assert {d['suites'][k]['n'].lower() for k in x['s']}|{t.lower() for t in x['a']}==cites,(ac['slug'],fid)
  for u in x['ly']:assert re.sub(r"^Académie (?:de |d')",'',ac['nom']) in departures[fid,u]
 keys=set()
 for f in d['suites'].values():
  for e in f['e']:
   assert d['region'] in regions[f['o'],e['o']]
   assert e['af'].startswith('https://www.onisep.fr/')
   if e['ij']:
    for x in e['ij']['v'] if 'v' in e['ij'] else [e['ij']]:
     assert set(x)<={'p','e','r'} and x.get('r',None) in {None,'récente','précédente'}
     for k in 'pe':assert x[k] is None or 0<=x[k]<=100
    if 'v' in e['ij']:assert [x['r'] for x in e['ij']['v']]==['récente','précédente']
   k=f['o'].split('.')[-1]+'|'+e['o'].split('.')[-1];keys.add(k)
   if k not in ps['f']:continue
   x=ps['f'][k];r=psraw[x['g']];assert meme_bts(f['n'],r['fil_lib_voe_acc'])
   g=r['g_olocalisation_des_formations'];distance=km(e['lat'],e['lon'],g['lat'],g['lon']);assert distance<.1 or (distance<2 and nom_proche(e['n'],r['g_ea_lib_vx'],distance))
   assert [x[k] for k in ['pl','c','a','bp']]==[r[k] for k in ['capa_fin','voe_tot','acc_tot','acc_bp']]
   if norm(e['n'])!=norm(r['g_ea_lib_vx']):
    review=revues[e['o']+'|'+str(x['g'])];assert review['decision']=='confirme';assert review['uai_parcoursup'] in review['uai_onisep']
   n+=1
 assert set(ps['f'])<=keys
 assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',path.read_text()),'Adresse électronique dans les données'
for r in json.loads((ROOT/'formation/data/bilan-parcoursup.json').read_text())['rapprochements']:
 if r['statut'] in ('ambigu','nom_a_verifier'):
  for ac in json.loads((ROOT/'commun/academies.json').read_text()):
   if ac['region']==r['region']:assert r['cle'] not in json.loads((ROOT/'formation/data'/f"{ac['slug']}-parcoursup.json").read_text())['f']
for name in ['aide/aide.json','apres-3e/apres3e.json','formation/formations.json','formation/parcoursup.json']:
 assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','origin/main:'+name],cwd=ROOT)
assert not subprocess.check_output(['git','diff','origin/main','--','commun/'],cwd=ROOT)
print(f'30 académies : diplômes et lieux sourcés, poursuites citées, régions respectées ; {n} lignes Parcoursup conformes aux sources ; ambiguïtés absentes ; JSON historiques et commun/ inchangés.')
