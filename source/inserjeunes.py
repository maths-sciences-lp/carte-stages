import json,re,unicodedata,difflib
def norm(s):
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    s=re.sub(r"[^a-z0-9 ]"," ",s); return re.sub(r"\s+"," ",s).strip()
TYP={'bac pro':'BAC PRO','cap':'CAP','capa':'CAP','cap agricole':'CAP','bts':'BTS','bma':'BMA','cs':'MC4','mc':'MC4'}
def split(l):
    n=norm(l)
    for p in sorted(TYP,key=len,reverse=True):
        if n.startswith(p+' '): return TYP[p],n[len(p)+1:]
    return None,n
IJ={}
for r in json.load(open('ij.json')):
    if r['annee']!='cumul 2023-2024': continue
    if r['taux_poursuite_etudes'] is None and r['taux_emploi_6_mois'] is None: continue
    t=r['type_diplome']; t='MC4' if t in('MC4','MC5','CS') else t
    IJ.setdefault(r['uai'],[]).append((t,norm(r['libelle_formation']),r))
def cherche(uai,libelle):
    t,n=split(libelle)
    if not t or uai not in IJ: return None
    best=None;bs=0
    for tt,nn,r in IJ[uai]:
        if tt!=t: continue
        s=1.0 if nn==n else difflib.SequenceMatcher(None,nn,n).ratio()
        if s<1 and ('option' in nn or 'option' in n):
            oa=nn.split('option',1)[1] if 'option' in nn else ''; ob=n.split('option',1)[1] if 'option' in n else ''
            oa=re.sub(r'^ [a-e] ',' ',oa); ob=re.sub(r'^ [a-e] ',' ',ob)
            if difflib.SequenceMatcher(None,oa,ob).ratio()<0.95: continue
        if s>bs: bs,best=s,r
    if best and bs>=0.95:
        return dict(p=best['taux_poursuite_etudes'],e=best['taux_emploi_6_mois'])
    return None
