import json,re
p=json.load(open('prospects.json'))
NAFL={'43.22A':'Plomberie, chauffage','43.22B':'Climatisation, froid, ventilation','35.30Z':'Production et réseaux de chaleur et de froid','33.20B':'Installation de machines (génie climatique)',
 '43.32A':'Menuiserie bois','43.32C':'Agencement de magasins','16.23Z':'Charpente, menuiserie industrielle','41.20A':'Construction, rénovation','41.20B':'Construction, rénovation',
 '43.99C':'Travaux de bâtiment','43.29A':'Isolation','43.34Z':'Peinture, finitions','43.39Z':'Finitions du bâtiment','74.10Z':'Design, décoration',
 '31.09B':'Ébénisterie, fabrication de meubles','31.09A':'Sièges et meubles d’ameublement','31.01Z':'Meubles de bureau et de magasin','95.24Z':'Restauration de meubles',
 '18.12Z':'Imprimerie','18.13Z':'Prépresse, gravure','73.11Z':'Communication, publicité','73.12Z':'Régie publicitaire','25.99B':'Fabrication d’enseignes métalliques',
 '27.40Z':'Enseignes lumineuses','23.19Z':'Enseignes en verre, plexiglas','43.29B':'Pose d’enseignes, installations','43.21A':'Pose d’enseignes lumineuses',
 '71.12A':'Géomètre-expert, topographie','74.90A':'Économiste de la construction','71.12B':'Bureau d’études techniques'}
EFF={'01':'1 ou 2 salariés','02':'3 à 5 salariés','03':'6 à 9 salariés','11':'10 à 19 salariés','12':'20 à 49 salariés','21':'50 à 99 salariés','22':'100 à 199 salariés',
 '31':'200 à 249 salariés','32':'250 à 499 salariés','41':'500 à 999 salariés','42':'1 000 à 1 999 salariés','51':'2 000 à 4 999 salariés','52':'5 000 à 9 999 salariés','53':'10 000 salariés et plus'}
pts=[]
for r in p:
    if r['nj']=='1000' or r['diff_ul']!='O' or r['diff_et']!='O' or not r['la']: continue
    nom=re.sub(r'\s+',' ',r['nom']).strip()
    d=dict(n=nom,e=r['ens'] if r['ens'] and r['ens'].upper() not in nom.upper() else '',f=r['fil'],a=NAFL.get(r['naf'],''),ad=r['adr'],
           s=r['siret'],t=EFF.get(r['eff'],''),r=1 if r['rge'] else 0,la=round(float(r['la']),5),lo=round(float(r['lo']),5))
    pts.append({k:v for k,v in d.items() if v})
pts.sort(key=lambda x:x['n'])
html=open('public_template.html').read().replace('/*DATA*/',json.dumps(pts,ensure_ascii=False,separators=(',',':')))
for path in ['../index.html']: open(path,'w').write(html)
import collections; print(len(pts),collections.Counter(x['f'] for x in pts),len(html)//1024,'Ko')
