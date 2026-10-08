"""Comptages reproductibles sur les deux instantanés, sans requête distante."""
from pathlib import Path
import json,math,urllib.parse,re
IDF=['75','77','78','91','92','93','94','95']
SHORT=['tne','mnb','mama','iccer','mee','tma','era','eeb','geometre','mit','sdg','ebeniste','bma-ebeniste','bma-signaletique','ma']
EXTRA=['cap-cuisine','cap-boulanger','cap-patissier','cap-accompagnant-educatif-petite-enfance','bac-pro-accompagnement-soins-et-services-a-la-personne']
def comparer(root,national):
 R,N=Path(root),Path(national)
 forms=json.loads((R/'data/index.json').read_text())['formations']
 nf={x['k']:x for x in json.loads((N/'catalogue.json').read_text())['formations']}
 proof_path=R/'source/verification-idf-national/entreprises-api.json'
 proof=json.loads(proof_path.read_text()) if proof_path.exists() else {}
 aliases=json.loads((R/'stage/aliases-idf.json').read_text())
 items=[{'adresse':'/'+x,'cible':re.search(r'location.replace\("([^"\n]+)',(R/x/'index.html').read_text()).group(1)} for x in SHORT]+[{'cle':x} for x in EXTRA]
 def distance(r):
  lat,lon=map(math.radians,r[3:5]);a,b=map(math.radians,[48.874884,2.430721]);return 12742*math.asin(math.sqrt(math.sin((lat-a)/2)**2+math.cos(a)*math.cos(lat)*math.sin((lon-b)/2)**2))
 def rows(keys,national):
  out={}
  for k in keys:
   paths=[N/'sirene'/d/(k+'.json') for d in ['75','77','78','91','92','93','94','95']] if national else [R/'data'/(k+'.json')]
   for p in paths:
    for r in json.loads(p.read_text()):out.setdefault(r[7],r)
  return out
 counts=[];missing={};allnew={}
 for p in (N/'sirene').glob('*/*.json'):
  if p.parent.name in ['75','77','78','91','92','93','94','95']:
   for r in json.loads(p.read_text()):allnew.setdefault(r[7],[]).append(p.stem)
 for item in items:
  key=item.get('cle') or urllib.parse.parse_qs(item['cible'].split('#')[1])['f'][0];f=next(f for f in forms if f['k']==key);g=nf[aliases.get(key,key)];old=rows(f['s'],False);new=rows(g['s'],True)
  for radius in [0,5]:
   x={s:r for s,r in old.items() if not radius or distance(r)<=radius};y={s:r for s,r in new.items() if not radius or distance(r)<=radius};rem=set(x)-set(y);add=set(y)-set(x)
   causes={};evidence=[]
   for s in sorted(rem):
    if s in new:reason='Coordonnées : hors du rayon dans le nouveau fichier'
    elif s in allnew:reason='Autre secteur dans le nouveau classement'
    else:
     missing[s]=x[s];e=proof.get(s,{}).get('resultat') or [{}];e=e[0]
     if e.get('etat')=='F':reason='Fermé lors du contrôle API du 08/10/2026'
     elif e.get('diffusion') and e['diffusion']!='O':reason='Diffusion restreinte lors du contrôle API'
     elif e.get('etat')=='A':reason='Actif par SIRET, absent du relevé départemental API (cause interne non établie)'
     else:reason='Absent du nouveau relevé API (statut non établi)'
    causes[reason]=causes.get(reason,0)+1;evidence.append({'siret':s,'raison':reason,'secteurs_apres':sorted(set(allnew.get(s,[])))})
   counts.append(dict(adresse=item.get('adresse','/#f='+key),cle=key,rayon=radius,avant=len(x),apres=len(y),ajouts=len(add),retraits=len(rem),causes=causes,details=evidence))
 return counts
