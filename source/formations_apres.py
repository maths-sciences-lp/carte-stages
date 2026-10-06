import csv,json,collections
from suites import SUITES
def load(f): return [x for x in csv.DictReader(open(f,encoding='utf-8-sig'),delimiter=';') if x.get('ENS région','') in ('Ile-de-France','Île-de-France')]
rows=load('sup2.csv')+load('605340ddc19a9.csv')
by=collections.defaultdict(list)
for x in rows: by[x['Formation (FOR) libellé'].lower()].append(x)
def cap1(s): return s[:1].upper()+s[1:]
out={'date':'6 octobre 2026','lycee':{'n':'Lycée Eugène Hénaff','lat':48.874884,'lon':2.430721},'classes':[]}
statuts=collections.Counter()
for k,(court,lib,forid,suites) in SUITES.items():
    cl={'k':k,'n':court,'lib':cap1(lib),'onisep':'https://www.onisep.fr/http/redirection/formation/slug/'+forid,'f':[],'ailleurs':[]}
    for s in suites:
        L=by.get(s.lower(),[])
        if not L: cl['ailleurs'].append(cap1(s)); continue
        seen={};f=None
        for x in L:
            try: lat=float(x['ENS latitude']);lon=float(x['ENS longitude'])
            except: continue
            u=x['ENS code UAI'] or x["Lieu d'enseignement (ENS) libellé"]
            if u in seen: continue
            statuts[x['ENS statut']]+=1
            seen[u]=dict(n=x["Lieu d'enseignement (ENS) libellé"],st=x['ENS statut'],a=x['ENS adresse'],cp=x['ENS code postal'],v=x['ENS commune'],
                lat=round(lat,5),lon=round(lon,5),w=x['ENS site web'],o=x['ENS URL et ID Onisep'],h=x['ENS hébergement'],af=x['AF page web'])
            f=f or dict(n=cap1(s),t=x['FOR type'],o=x['FOR URL et ID Onisep'],d=x['AF durée cycle standard'])
        f['e']=list(seen.values()); cl['f'].append(f)
    out['classes'].append(cl)
json.dump(out,open('formations.json','w'),ensure_ascii=False,separators=(',',':'))
print(statuts); import os; print(os.path.getsize('formations.json'))
for c in out['classes']: print(c['n'], [ (f['n'][:30],len(f['e'])) for f in c['f']], 'ailleurs:',len(c['ailleurs']))
