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

from apres_lycee import TYPES, construire, load
from formation_collecte import fiches

ROOT=Path(__file__).resolve().parents[1]
IJ_URL='https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-inserjeunes-lycee_pro-formation-fine/exports/json?'+urllib.parse.urlencode(dict(
    where='annee="cumul 2023-2024"',select='annee,uai,type_diplome,libelle_formation,code_formation_mefstat11,taux_poursuite_etudes,taux_emploi_6_mois'))


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


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--academies',nargs='+',required=True,help='Slugs du catalogue commun ou toutes')
    p.add_argument('--sources',type=Path,default=Path.cwd(),help='605340ddc19a9.csv, sup2.csv et fiches historiques')
    p.add_argument('--cache',type=Path,default=Path.home()/'.cache/carte-stages-formation')
    args=p.parse_args();src=args.sources.resolve();cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((ROOT/'commun/academies.json').read_text())
    selected={a['slug'] for a in catalog} if args.academies==['toutes'] else set(args.academies)
    if selected-{a['slug'] for a in catalog}:p.error('Académie inconnue')
    lycee=load(src/'605340ddc19a9.csv',regions=())
    sup=load(src/'sup2.csv',regions=())
    names={re.sub(r"^Académie (?:de |d')",'',a['nom']) for a in catalog if a['slug'] in selected}
    ids={r['FOR URL et ID Onisep'].rsplit('.',1)[-1] for r in lycee if r['ENS académie'] in names and r['FOR type'] in TYPES}
    journal=fiches(ids,src,cache)
    json_export(IJ_URL,cache/'ij.json')
    os.chdir(cache)
    from inserjeunes import IJ,split
    uncertain=set()

    def cherche(uai,libelle):
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
        values={(r['code_formation_mefstat11'],r['taux_poursuite_etudes'],r['taux_emploi_6_mois']) for _,r in candidates}
        if len(values)>1:uncertain.add((uai,libelle))
        if len(values)!=1:return None
        _,p,e=next(iter(values));return dict(p=p,e=e)

    excluded=[];no_uai=set();urls=set()
    def prepare(rows):
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
                inserjeunes_url=IJ_URL,inserjeunes_ambigus=[dict(uai=u,formation=l) for u,l in sorted(uncertain)],
                sans_uai=sorted(no_uai),urls_omises=sorted(urls),exclusions=excluded)
    (outdir/'bilan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
