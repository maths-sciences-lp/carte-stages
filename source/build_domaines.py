import json,re,os,unicodedata,collections,sys
if '--national' in sys.argv:
    sys.argv.remove('--national')
    from stage_donnees import main
    main()
    sys.exit(0)
from domaines import DOMAINES, MOTS_CLES, MOTS_CLES_SOURCES, SOURCES_MOTS_CLES, FILTRES
from aides import ALIAS, ICON, FAMILLES, AUTRES, FAMILLES_SECTEURS
from adresses import nettoie
OUT=sys.argv[1] if len(sys.argv)>1 else 'www2'
os.makedirs(OUT+'/data',exist_ok=True)
def slug(s):
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:60]
code2=[]; sec_of={}
index=[]
for d,secs in DOMAINES.items():
    ent={'d':d,'i':ICON.get(d,''),'s':[]}
    for s,codes in secs.items():
        k=slug(s); ent['s'].append({'n':s,'k':k})
        for c in codes: sec_of.setdefault(c,k)
    index.append(ent)
EFF={'01':'1 ou 2 salariés','02':'3 à 5 salariés','03':'6 à 9 salariés','11':'10 à 19 salariés','12':'20 à 49 salariés','21':'50 à 99 salariés','22':'100 à 199 salariés',
 '31':'200 à 249 salariés','32':'250 à 499 salariés','41':'500 à 999 salariés','42':'1 000 à 1 999 salariés','51':'2 000 à 4 999 salariés','52':'5 000 à 9 999 salariés','53':'10 000 salariés et plus'}
EK=list(EFF)
by=collections.defaultdict(dict); skip=collections.Counter()
FILT={slug(n):re.compile(rx) for n,rx in FILTRES.items()}
for line in open('idf/etablissements.jsonl'):
    r=json.loads(line)
    if r['nj']=='1000': skip['EI']+=1; continue
    if r['du']!='O' or r['de']!='O': skip['non diffusible']+=1; continue
    if not r['la']: skip['sans position']+=1; continue
    k=sec_of.get(r['c']) or sec_of.get(r['q'])
    if k in FILT and not FILT[k].search((r['n']+' '+(r['e'] or '')).upper()):
        k=sec_of.get(r['q']) if r['q']!=r['c'] else None
        if not k: skip['hors filtre']+=1; continue
    nom=re.sub(r'\s+',' ',r['n']).strip(); nom=re.sub(r'(\([^()]*\))(\s*\1)+',r'\1',nom); nom=re.sub(r'^(.+?) \(\1\)$',r'\1',nom); ens=r['e'] if r['e'] and r['e'].upper() not in nom.upper() else ''
    ens=ens.split(', ')[0] if ens else ''
    adr,rep=nettoie(r['ad'] or '')
    if adr: adr=adr[0].upper()+adr[1:]
    by[k][r['s']]=[nom,ens,adr,round(float(r['la']),5),round(float(r['lo']),5),EK.index(r['t'])+1 if r['t'] in EFF else 0,1 if r['r'] else 0,r['s'],rep]
# secteurs complétés par mots-clés (noms et enseignes), seulement depuis les domaines techniques
src={slug(x) for d,secs in DOMAINES.items() if d in SOURCES_MOTS_CLES for x in secs}
ajouts={}
for nomsec,rx in MOTS_CLES.items():
    k=slug(nomsec); rxc=re.compile(rx); n0=len(by.get(k,{}))
    ok={slug(x) for x in MOTS_CLES_SOURCES.get(nomsec,[])} or src
    for sec,rows in list(by.items()):
        if sec==k or sec not in src or sec not in ok: continue
        for sir,row in rows.items():
            t=(row[0]+' '+row[1]).upper()
            if rxc.search(t) and 'ENSEIGNEMENT' not in t: by[k][sir]=row
    ajouts[nomsec]=len(by[k])-n0
print('ajouts par mots-clés :',ajouts)
tot=0
for ent in index:
    for s in ent['s']:
        rows=sorted(by.get(s['k'],{}).values()); s['c']=len(rows); tot+=len(rows)
        json.dump(rows,open(f"{OUT}/data/{s['k']}.json",'w'),ensure_ascii=False,separators=(',',':'))
M=json.load(open('formation_secteurs.json'))
name2k={s['n']:s['k'] for e in index for s in e['s']}
forms=[]
for n,secs in sorted(M.items(),key=lambda x:x[0].lower()):
    t='CAP' if n.startswith('CAP') else 'Bac pro'
    court=n[4:] if n.startswith('CAP ') else n[5:] if n.startswith('CAPa ') else n[8:] if n.startswith('bac pro ') else n
    forms.append({'n':court[0].upper()+court[1:],'t':t+('a' if n.startswith('CAPa') else ''),'s':[name2k[x] for x in secs],'a':ALIAS.get(n,''),'k':slug(n)})
for n,(a,lst) in FAMILLES.items():
    secs=[name2k[x] for x in FAMILLES_SECTEURS[n]] if n in FAMILLES_SECTEURS else list(dict.fromkeys(name2k[x] for b in lst for x in M[b]))
    forms.append({'n':n,'t':'2nde pro','s':secs,'a':a,'k':slug('2nde '+n)})
for n,(t,a,secs) in AUTRES.items():
    forms.append({'n':n,'t':t,'s':[name2k[x] for x in secs],'a':a,'k':slug(t+' '+n)})
json.dump({'domaines':index,'formations':forms,'eff':list(EFF.values()),'date':'5 octobre 2026'},open(f'{OUT}/data/index.json','w'),ensure_ascii=False,separators=(',',':'))
print(tot,dict(skip))

# Lycées d'Île-de-France qui proposent un CAP ou un bac pro (effectifs 2025 + annuaire de l'éducation)
_a={r['identifiant_de_l_etablissement']:r for r in json.load(open('annuaire_idf.json'))}
_u={r['numero_d_etablissement'] for r in json.load(open('lp_idf_2025.json'))}
_ly=[]
for u in sorted(_u):
    r=_a.get(u)
    if not r or not r.get('latitude'): continue
    _ly.append({'u':u,'n':r['nom_etablissement'],'c':r['nom_commune'],'p':r['code_postal'],'la':round(r['latitude'],6),'lo':round(r['longitude'],6)})
_ly.sort(key=lambda x:(x['c'],x['n']))
json.dump(_ly,open(f'{OUT}/data/lycees.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(_ly),'lycées')
