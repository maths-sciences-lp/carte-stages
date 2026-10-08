import csv,json,re,collections
from domaines_apres3e import DOM,domaines
from corrections_apres3e import C
T={'classe de 2de professionnelle':'2de pro','CAP':'CAP','CAP agricole':'CAP','baccalauréat professionnel':'Bac pro'}
# Académies d'Île-de-France (Créteil d'abord : les adresses et les liens existants n'en dépendent pas)
ACADS=('Créteil','Paris','Versailles')
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
# Internat : fiche Onisep du lycée (texte) croisée avec l'annuaire de l'Éducation nationale (champ hebergement).
import os,urllib.request,urllib.parse
def annuaire_hebergement(uais,fichier='annuaire_hebergement.json'):
    res=json.load(open(fichier)) if os.path.exists(fichier) else {}
    uais=[u for u in uais if u not in res]
    for i in range(0,len(uais),50):
        q="identifiant_de_l_etablissement in ("+",".join('"%s"'%u for u in uais[i:i+50])+")"
        url="https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/records?"+urllib.parse.urlencode(dict(where=q,select="identifiant_de_l_etablissement,hebergement",limit=100))
        for r in json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60))['results']:
            res[r['identifiant_de_l_etablissement']]=r['hebergement']
    json.dump(res,open(fichier,'w')); return res
def internat(uai,o,HEB):
    """'i' internat au lycée, 'a' internat dans un autre lycée, 'v' sources en désaccord ; None sinon. Plus les conditions Onisep."""
    o=(o or '').strip(); a=HEB.get(uai)
    if 'hospitalisation' in o or re.search(r'réservé aux sections|réservés à des élèves de BTS',o): return None,''
    ailleurs='hors établissement' in o or 'internat délocalisé' in o
    sur_place=o.startswith('internat') and not re.match(r'internat \(homme/femme - hors établissement',o)
    m=re.search(r'\((?:homme/femme|homme|femme)\s*-\s*(.*)\)',o)
    cond=m.group(1).strip() if m else ''
    if o.startswith('internat (homme)'): cond=('garçons'+(' ; '+cond if cond else ''))
    if sur_place and a==1: return 'i',cond
    if ailleurs and not sur_place: return 'a',cond
    if sur_place or a==1: return 'v',cond
    return None,''

def construire(rows,HEB,cols,cherche,pression=(),date='6 octobre 2026'):
    """Même construction et même ordre de champs dans les deux modes."""
    # Affectation 2025 : premiers vœux et places (Draio Créteil, voir pression.py), reliés aux intitulés
    # Onisep par pression_correspondance.json. « pc » : places communes à plusieurs CAP du lycée (offre d'affectation regroupée).
    PRESS={}
    if pression:
        _corr=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pression_correspondance.json')))
        _par_uai=collections.defaultdict(set)
        for x in rows: _par_uai[x['ENS code UAI']].add(x['Formation (FOR) libellé'])
        for p in pression:
            cible=_corr.get(p['l'])
            if cible is None: continue
            if isinstance(cible,dict):
                libs=[l for l in _par_uai[p['u']] if re.search(cible['commun'],l)]
            else:
                libs=[cible] if cible in _par_uai[p['u']] else []
            for l in libs: PRESS[(p['u'],l)]=dict(v=p['v'],c=p['c'],**({'pc':1} if len(libs)>1 else {}))
    # Durée : un même diplôme dure 1 an dans un lycée, 2 ans dans un autre (voire les deux dans le même).
    # On garde la durée de chaque lycée, et pour la formation la plus fréquente (duv=1 quand elle varie).
    DUR=collections.defaultdict(list)
    for x in rows:
        k=(x['ENS code UAI'] or x["Lieu d'enseignement (ENS) libellé"],x['Formation (FOR) libellé']); du=x['AF durée cycle standard']
        if du not in DUR[k]: DUR[k].append(du)
    def duree(k): return ' ou '.join(sorted(DUR[k]))
    par_duree=getattr(cherche,'par_duree',False)
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
            dep=x['ENS département'],ac=x['ENS académie'],lat=round(lat,5),lon=round(lon,5),w=x['ENS site web'],o=x['ENS URL et ID Onisep'],h=x['ENS hébergement'],af=x['AF page web'],c=frais(x['AF coût scolarité']),
            ij=cherche(x['ENS code UAI'],l,DUR[(u,l)]) if par_duree else cherche(x['ENS code UAI'],l))
        f['e'][u]['du']=duree((u,l))
        it,ic=internat(x['ENS code UAI'],x['ENS hébergement'],HEB)
        pr=PRESS.get((x['ENS code UAI'],l))
        if pr: f['e'][u]['p']=pr
        if it: f['e'][u]['it']=it
        if it and ic: f['e'][u]['ic']=ic
    for f in F.values():
        n=collections.Counter(e['du'] for e in f['e'].values())
        if n:
            f['du']=max(n,key=lambda k:(n[k],k))
            if len(n)>1: f['duv']=1
        for e in f['e'].values():
            if e['du']==f['du']: del e['du']
    out=dict(date=date,domaines=[dict(k=k,i=i,n=n,s=s) for k,i,n,s,_,_ in DOM],
      formations=[dict(f,e=list(f['e'].values())) for f in sorted(F.values(),key=lambda f:({'2de pro':0,'Bac pro':1,'CAP':2}[f['t']],f['n']))])
    # Ordre alphabétique (nom, commune) : les suggestions de collèges ne dépendent plus de l'ordre de l'export.
    out['colleges']=sorted([dict(n=c['nom_etablissement'],v=' '.join(c['nom_commune'].split()),lat=round(c['latitude'],5),lon=round(c['longitude'],5)) for c in cols if c.get('latitude')],key=lambda c:(c['n'],c['v']))
    # mots que tapent les élèves (sigles, métiers) : mêmes listes que « Trouve ton stage »
    from aides import ALIAS, FAMILLES
    _AL={k.lower():v for k,v in ALIAS.items()}
    def alias(n):
        a=_AL.get(n.lower(),'')
        for k,(al,_) in FAMILLES.items():
            if k.split(' (')[0].lower() in n.lower(): a+=' '+al
        return a.strip()
    for f in out['formations']:
        al=alias(f['n'])
        if al: f['al']=al
    return out

def historique():
    """Sans paramètre : sources du dossier courant, sortie historique inchangée."""
    from inserjeunes import cherche
    rows=[x for x in csv.DictReader(open('605340ddc19a9.csv',encoding='utf-8-sig'),delimiter=';') if x['ENS académie'] in ACADS and x['FOR type'] in T]
    heb=annuaire_hebergement(sorted({x['ENS code UAI'] for x in rows if x['ENS code UAI']}))
    cols=json.load(open('colleges_idf.json' if os.path.exists('colleges_idf.json') else 'colleges.json'))
    pression=json.load(open('pression_2025.json')) if os.path.exists('pression_2025.json') else []
    out=construire(rows,heb,cols,cherche,pression)
    with open('apres3e.json','w') as f: json.dump(out,f,ensure_ascii=False,separators=(',',':'))
    print(os.path.getsize('apres3e.json'),'octets ; formations',len(out['formations']),'lieux',sum(len(f['e']) for f in out['formations']),'collèges',len(out['colleges']))

if __name__=='__main__':
    import sys
    if len(sys.argv)==1:
        historique()
    else:
        from apres3e_national import main
        main()
