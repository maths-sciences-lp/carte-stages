import csv,json,re,collections
from domaines_apres3e import DOM,domaines
from corrections_apres3e import C
T={'classe de 2de professionnelle':'2de pro','CAP':'CAP','CAP agricole':'CAP','baccalauréat professionnel':'Bac pro'}
rows=[x for x in csv.DictReader(open('605340ddc19a9.csv',encoding='utf-8-sig'),delimiter=';') if x['ENS académie']=='Créteil' and x['FOR type'] in T]
def nom(l):
    l=re.sub(r'^classe de 2de professionnelle ','2de pro ',l)
    l=re.sub(r'^CAPa ','CAP agricole ',l)
    return l[:1].upper()+l[1:]
def frais(s):
    s=(s or '').strip()
    m=re.search(r'\((\d+) euros par an(.*?)\)',s)
    if m:
        n=f"{int(m.group(1)):,}".replace(',',' '); r=m.group(2).strip(' ,')
        return f"{n} € par an"+(f" ({r})" if r else '')
    return s
F={}
for x in rows:
    l=x['Formation (FOR) libellé']
    f=F.get(l)
    if not f:
        d=C[l].split(',') if l in C else domaines(l,x['FOR indexation domaine web Onisep'])
        f=F[l]=dict(n=nom(l),t=T[x['FOR type']],d=d,o=x['FOR URL et ID Onisep'],du=x['AF durée cycle standard'],e={})
    try: lat=float(x['ENS latitude']);lon=float(x['ENS longitude'])
    except: continue
    u=x['ENS code UAI'] or x["Lieu d'enseignement (ENS) libellé"]
    if u in f['e']: continue
    f['e'][u]=dict(n=x["Lieu d'enseignement (ENS) libellé"],st=x['ENS statut'],a=x['ENS adresse'],cp=x['ENS code postal'],v=x['ENS commune'],
        dep=x['ENS département'],lat=round(lat,5),lon=round(lon,5),w=x['ENS site web'],o=x['ENS URL et ID Onisep'],h=x['ENS hébergement'],af=x['AF page web'],c=frais(x['AF coût scolarité']))
out=dict(date='6 octobre 2026',domaines=[dict(k=k,i=i,n=n,s=s) for k,i,n,s,_,_ in DOM],
  formations=[dict(f,e=list(f['e'].values())) for f in sorted(F.values(),key=lambda f:({'2de pro':0,'Bac pro':1,'CAP':2}[f['t']],f['n']))])
cols=json.load(open('colleges.json'))
out['colleges']=[dict(n=c['nom_etablissement'],v=c['nom_commune'],lat=round(c['latitude'],5),lon=round(c['longitude'],5)) for c in cols if c.get('latitude')]
json.dump(out,open('apres3e.json','w'),ensure_ascii=False,separators=(',',':'))
import os;print(os.path.getsize('apres3e.json'),'formations',len(out['formations']),'lieux',sum(len(f['e']) for f in out['formations']),'colleges',len(out['colleges']))
print(collections.Counter(k for f in out['formations'] for k in f['d']))
print(collections.Counter(f['t'] for f in out['formations']))
