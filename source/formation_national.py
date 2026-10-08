"""Après le lycée : académies de départ, poursuites dans leur région académique."""
import argparse
import collections
import datetime
import difflib
import gzip
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import urllib.parse

from apres_lycee import TYPES, construire, lieu, load
from formation_collecte import fiches

ROOT=Path(__file__).resolve().parents[1]
IJ_URL='https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-inserjeunes-lycee_pro-formation-fine/exports/json?'+urllib.parse.urlencode(dict(
    where='annee="cumul 2023-2024"',select='annee,uai,type_diplome,libelle_formation,code_formation_mefstat11,taux_poursuite_etudes,taux_emploi_6_mois'))
# Codes déjà publiés dans le cumul précédent : un code absent de cette liste est la
# version récente du diplôme (ex. BTS MS option B, 32221025015 apparu en 2023-2024).
IJ_PREC_URL='https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-inserjeunes-lycee_pro-formation-fine/exports/json?'+urllib.parse.urlencode(dict(
    where='annee="cumul 2022-2023"',select='code_formation_mefstat11',group_by='code_formation_mefstat11'))


def deux_versions(candidates,anciens):
    """Deux lignes InserJeunes au même intitulé exact, dans le même lycée, dont une seule
    a un code nouveau : les deux chiffres sont publiés, version récente d'abord.
    Sinon None (aucun chiffre, pas de choix au hasard ni de moyenne)."""
    exact={r['code_formation_mefstat11']:r for s,r in candidates if s==1}
    if len(exact)!=2 or len(candidates)!=2:return None
    recents=[c for c in exact if c not in anciens]
    if len(recents)!=1:return None
    ordre=[recents[0]]+[c for c in exact if c!=recents[0]]
    return [dict(p=exact[c]['taux_poursuite_etudes'],e=exact[c]['taux_emploi_6_mois'],r=r) for c,r in zip(ordre,('récente','précédente'))]


def json_export(url, path):
    if not path.exists():
        temp=path.with_suffix('.part')
        subprocess.run(['curl','--fail','--location','--retry','2','--max-time','180','--silent','--show-error','-A','Mozilla/5.0','-o',str(temp),url],check=True)
        json.loads(temp.read_text())
        temp.replace(path)
    return json.loads(path.read_text())


def route(nom):
    return '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Après le lycée – '''+html.escape(nom)+'''</title></head>
<body><p id="loading" role="status">Chargement des formations…</p>
<noscript>Active JavaScript pour choisir ton diplôme et voir les poursuites d’études.</noscript>
<script src="../ouvrir.js"></script></body></html>
'''


def valid(row):
    try:
        lat,lon=float(row['ENS latitude']),float(row['ENS longitude'])
        return math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180 and (lat,lon)!=(0,0)
    except (TypeError,ValueError):
        return False


def candidats(IJ,split,uai,libelle):
    """Lignes InserJeunes compatibles avec une formation d'un lycée (intitulé exact prioritaire)."""
    t,n=split(libelle);candidates=[]
    for tt,nn,r in IJ.get(uai,[]):
        if tt!=t:continue
        score=difflib.SequenceMatcher(None,nn,n).ratio()
        if score<.95:continue
        if nn!=n and ('option' in nn or 'option' in n):
            oa=re.sub(r'^ [a-e] ',' ',nn.split('option',1)[1]) if 'option' in nn else ''
            ob=re.sub(r'^ [a-e] ',' ',n.split('option',1)[1]) if 'option' in n else ''
            if difflib.SequenceMatcher(None,oa,ob).ratio()<.95:continue
        candidates.append((score,r))
    if any(s==1 for s,_ in candidates):candidates=[(s,r) for s,r in candidates if s==1]
    return candidates


def completer_inserjeunes(src,cache):
    """Ajoute les deux chiffres (deux_versions) aux fichiers déjà publiés, sans tout régénérer :
    mêmes sources (CSV Onisep, ij.json) et même règle que la fabrication."""
    src,cache=Path(src).resolve(),Path(cache).resolve()
    rows=load(src/'605340ddc19a9.csv',regions=())+load(src/'sup2.csv',regions=())
    lien={(r['ENS URL et ID Onisep'],r['FOR URL et ID Onisep']):(r['ENS code UAI'],r['Formation (FOR) libellé']) for r in rows if r['ENS code UAI']}
    json_export(IJ_URL,cache/'ij.json')
    anciens={r['code_formation_mefstat11'] for r in json_export(IJ_PREC_URL,cache/'ij-codes-2022-2023.json')}
    here=os.getcwd();os.chdir(cache)
    from inserjeunes import IJ,split
    os.chdir(here)
    outdir=ROOT/'formation/data';resolus=set();total=0
    for path in sorted(outdir.glob('*.json')):
        if path.name.startswith(('bilan','ile-de-france')) or path.name.endswith('-parcoursup.json'):continue
        data=json.loads(path.read_text());n=0
        for f in data['suites'].values():
            for e in f['e']:
                if e.get('ij') or (e['o'],f['o']) not in lien:continue
                uai,libelle=lien[(e['o'],f['o'])]
                v=deux_versions(candidats(IJ,split,uai,libelle),anciens)
                if v:e['ij']=dict(v=v);n+=1;resolus.add((uai,libelle))
        if n:path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
        total+=n;print(path.stem,n)
    bilan=outdir/'bilan.json';b=json.loads(bilan.read_text())
    b['inserjeunes_ambigus']=[x for x in b['inserjeunes_ambigus'] if (x['uai'],x['formation']) not in resolus]
    b['inserjeunes_deux_versions']=[dict(uai=u,formation=l) for u,l in sorted(resolus)]
    b['inserjeunes_prec_url']=IJ_PREC_URL
    bilan.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
    reunir_idf(outdir)
    print('lieux avec deux chiffres :',total,'· couples lycée/formation :',len(resolus))


def fabrique_cherche(IJ,split,anciens,uncertain):
    """InserJeunes d'un lycée pour une formation : un chiffre, deux versions, ou rien."""
    def cherche(uai,libelle):
        candidates=candidats(IJ,split,uai,libelle)
        values={(r['code_formation_mefstat11'],r['taux_poursuite_etudes'],r['taux_emploi_6_mois']) for _,r in candidates}
        if len(values)>1:
            v=deux_versions(candidates,anciens)
            if v:return dict(v=v)
            uncertain.add((uai,libelle))
        if len(values)!=1:return None
        _,p,e=next(iter(values));return dict(p=p,e=e)
    return cherche


def preparer(rows,excluded,no_uai,urls):
    """Lignes Onisep publiables : coordonnées valides, hors Monaco, sans courriel."""
    result=[]
    for x in rows:
        if not valid(x) or x['ENS commune']=='Monaco':
            excluded.append(dict(n=x["Lieu d'enseignement (ENS) libellé"],o=x['ENS URL et ID Onisep'],motif='Coordonnées invalides ou territoire de Monaco hors catalogue'))
            continue
        x=x.copy()
        if not x['ENS code UAI']:
            no_uai.add(x['ENS URL et ID Onisep'])
            # Identifiant local explicite ; jamais présenté comme un UAI réel.
            x['ENS code UAI']='onisep:'+x['ENS URL et ID Onisep'].rsplit('.',1)[-1]
        for k in ['ENS site web','AF page web','ENS hébergement','AF coût scolarité']:
            if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',x[k]):
                urls.add(x['ENS URL et ID Onisep']);x[k]=''
        result.append(x)
    return result


def toute_la_france(src,cache):
    """« Chercher dans toute la France » : un fichier par poursuite d'études (data/france/<id>.json),
    tous les lieux de France, mêmes règles que les pages d'académie, chiffres Parcoursup joints (ps).
    Poursuites = celles proposées dans au moins une académie (fichiers d'académie existants)."""
    src,cache=Path(src).resolve(),Path(cache).resolve()
    outdir=ROOT/'formation/data'
    lycee=load(src/'605340ddc19a9.csv',regions=());sup=load(src/'sup2.csv',regions=())
    json_export(IJ_URL,cache/'ij.json')
    anciens={r['code_formation_mefstat11'] for r in json_export(IJ_PREC_URL,cache/'ij-codes-2022-2023.json')}
    here=os.getcwd();os.chdir(cache)
    from inserjeunes import IJ,split
    os.chdir(here)
    uncertain=set();excluded=[];no_uai=set();urls=set()
    cherche=fabrique_cherche(IJ,split,anciens,uncertain)
    rows=preparer(sup,excluded,no_uai,urls)+preparer(lycee,excluded,no_uai,urls)
    par_lib=collections.defaultdict(list)
    for x in rows:par_lib[x['Formation (FOR) libellé'].lower()].append(x)
    academies=[p for p in sorted(outdir.glob('*.json')) if not p.name.startswith(('bilan','ile-de-france')) and not p.name.endswith('-parcoursup.json')]
    cles={};ps={}
    for p in academies:
        for k,f in json.loads(p.read_text())['suites'].items():cles.setdefault(k,{c:f[c] for c in ('n','t','o','d')})
        q=p.with_name(p.stem+'-parcoursup.json')
        if q.exists():ps.update(json.loads(q.read_text())['f'])
    fr=outdir/'france';fr.mkdir(exist_ok=True)
    for old in fr.glob('*.json'):old.unlink()
    index={};stats=[]
    for k,tete in sorted(cles.items()):
        fo=tete['o'];seen={}
        for x in par_lib.get(k,[]):
            lat,lon=float(x['ENS latitude']),float(x['ENS longitude'])
            # Un même UAI peut couvrir plusieurs campus dans des régions différentes :
            # chaque fiche Onisep d'établissement reste un lieu.
            u=(x['ENS code UAI'] or x["Lieu d'enseignement (ENS) libellé"],x['ENS URL et ID Onisep'])
            if u in seen:continue
            e=lieu(x,lat,lon,cherche);e['af']=e['o']
            cle_ps=fo.rsplit('.',1)[-1]+'|'+e['o'].rsplit('.',1)[-1]
            if cle_ps in ps:e['ps']=ps[cle_ps]
            seen[u]=e
            if x['FOR URL et ID Onisep']!=fo:raise ValueError('Identifiant Onisep différent pour '+k)
        if not seen:continue
        fid=fo.rsplit('.',1)[-1]
        # Nom, type et durée : ceux des pages d'académie (même poursuite, même affichage).
        out=dict(tete,e=list(seen.values()))
        path=fr/(fid+'.json');path.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
        index[k]=fid;stats.append((len(seen),path.stat().st_size,len(gzip.compress(path.read_bytes(),mtime=0))))
    bilan=dict(date=datetime.date.today().isoformat(),poursuites=len(index),lieux=sum(n for n,_,_ in stats),
               plus_gros_gzip=max(g for _,_,g in stats),total_gzip=sum(g for _,_,g in stats),
               inserjeunes_ambigus=len(uncertain),exclusions=len(excluded))
    (fr/'bilan.json').write_text(json.dumps(bilan,ensure_ascii=False,indent=2)+'\n')
    print(bilan)


IDF=('creteil','paris','versailles')


def reunir_idf(outdir=None):
    """Page /formation/ (Île-de-France) : un seul fichier, réuni à partir des trois
    fichiers d'académie (mêmes données, mêmes règles). Les poursuites sont régionales :
    les réunir évite de télécharger trois fois les mêmes lieux."""
    outdir=outdir or ROOT/'formation/data'
    if not all((outdir/f'{s}.json').exists() for s in IDF):return
    L=[json.loads((outdir/f'{s}.json').read_text()) for s in IDF]
    dip={}
    for d in L:
        for k,x in d['dip'].items():
            if k in dip:
                for c in ('ly','s','a'):dip[k][c]+=[v for v in x[c] if v not in dip[k][c]]
            else:dip[k]={**x,'ly':list(x['ly']),'s':list(x['s']),'a':list(x['a'])}
    out=dict(date=L[0]['date'],henaff=L[0]['henaff'],classes=L[0]['classes'],region=L[0]['region'],academie='Île-de-France',
             lycees={k:v for d in L for k,v in d['lycees'].items()},dip=dict(sorted(dip.items(),key=lambda x:x[1]['lib'])),
             suites={k:v for d in L for k,v in d['suites'].items()})
    (outdir/'ile-de-france.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
    if all((outdir/f'{s}-parcoursup.json').exists() for s in IDF):
        P=[json.loads((outdir/f'{s}-parcoursup.json').read_text()) for s in IDF]
        ps=dict(session=P[0]['session'],f={k:v for x in P for k,v in x['f'].items()})
        (outdir/'ile-de-france-parcoursup.json').write_text(json.dumps(ps,ensure_ascii=False,separators=(',',':')))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--academies',nargs='+',help='Slugs du catalogue commun ou toutes')
    p.add_argument('--completer-inserjeunes',action='store_true',help='Ajoute seulement les chiffres « deux versions » aux fichiers existants')
    p.add_argument('--toute-la-france',action='store_true',help='Fabrique seulement data/france/ (un fichier par poursuite)')
    p.add_argument('--sources',type=Path,default=Path.cwd(),help='605340ddc19a9.csv, sup2.csv et fiches historiques')
    p.add_argument('--cache',type=Path,default=Path.home()/'.cache/carte-stages-formation')
    args=p.parse_args();src=args.sources.resolve();cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    if args.completer_inserjeunes:return completer_inserjeunes(src,cache)
    if args.toute_la_france:return toute_la_france(src,cache)
    if not args.academies:p.error('--academies est obligatoire')
    catalog=json.loads((ROOT/'commun/academies.json').read_text())
    selected={a['slug'] for a in catalog} if args.academies==['toutes'] else set(args.academies)
    if selected-{a['slug'] for a in catalog}:p.error('Académie inconnue')
    lycee=load(src/'605340ddc19a9.csv',regions=())
    sup=load(src/'sup2.csv',regions=())
    names={re.sub(r"^Académie (?:de |d')",'',a['nom']) for a in catalog if a['slug'] in selected}
    ids={r['FOR URL et ID Onisep'].rsplit('.',1)[-1] for r in lycee if r['ENS académie'] in names and r['FOR type'] in TYPES}
    journal=fiches(ids,src,cache)
    json_export(IJ_URL,cache/'ij.json')
    anciens={r['code_formation_mefstat11'] for r in json_export(IJ_PREC_URL,cache/'ij-codes-2022-2023.json')}
    os.chdir(cache)
    from inserjeunes import IJ,split
    uncertain=set();excluded=[];no_uai=set();urls=set()
    cherche=fabrique_cherche(IJ,split,anciens,uncertain)
    prepare=lambda rows:preparer(rows,excluded,no_uai,urls)

    lycee=prepare(lycee);sup=prepare(sup)
    outdir=ROOT/'formation/data';outdir.mkdir(parents=True,exist_ok=True)
    summary=[]
    for ac in catalog:
        if ac['slug'] not in selected:continue
        region=ac['region'];name=re.sub(r"^Académie (?:de |d')",'',ac['nom'])
        region_rows=[r for r in sup+lycee if r['ENS région'].replace('Ile-de-France','Île-de-France')==region]
        departure=[r for r in lycee if r['ENS académie']==name]
        out,missing=construire(departure,region_rows,(name,),cherche,str(cache/'fiches'),historique=False)
        if missing:raise ValueError('Fiches manquantes : '+str(missing))
        if not out['dip'] or not out['lycees']:raise ValueError('Académie vide : '+ac['slug'])
        out['date']=datetime.date.today().isoformat();out['region']=region;out['academie']=ac['nom']
        if out['henaff'] not in out['lycees']:out['classes']=[]
        # Le bouton « Fiche Onisep » doit ouvrir une fiche Onisep, pas AF page web
        # qui peut être le site commercial de l'établissement.
        for f in out['suites'].values():
            for e in f['e']:e['af']=e['o']
        file=outdir/(ac['slug']+'.json');file.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
        page=ROOT/'formation'/ac['slug']/'index.html';page.parent.mkdir(parents=True,exist_ok=True);page.write_text(route(ac['nom']))
        summary.append(dict(slug=ac['slug'],academie=name,region=region,diplomes=len(out['dip']),lycees=len(out['lycees']),poursuites=len(out['suites']),lieux=sum(len(f['e']) for f in out['suites'].values()),
                            octets=file.stat().st_size,gzip_octets=len(gzip.compress(file.read_bytes(),mtime=0)),sans_exemple=sum(not d['s'] and not d['a'] for d in out['dip'].values())))
        print(summary[-1],flush=True)
    page=ROOT/'formation/france/index.html';page.parent.mkdir(parents=True,exist_ok=True);page.write_text(route('France'))
    report=dict(date=datetime.date.today().isoformat(),academies=summary,fiches=journal,
                sources=[dict(nom=q.name,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),date=datetime.datetime.fromtimestamp(q.stat().st_mtime).isoformat(timespec='seconds')) for q in [src/'605340ddc19a9.csv',src/'sup2.csv',cache/'ij.json']],
                inserjeunes_url=IJ_URL,inserjeunes_prec_url=IJ_PREC_URL,inserjeunes_ambigus=[dict(uai=u,formation=l) for u,l in sorted(uncertain)],
                sans_uai=sorted(no_uai),urls_omises=sorted(urls),exclusions=excluded)
    (outdir/'bilan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    reunir_idf(outdir)
