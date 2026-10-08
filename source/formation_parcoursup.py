"""Rapprochements régionaux Parcoursup ; ambiguïtés et noms différents à contrôler."""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.parse

from parcoursup import API, decoupe, km, meme_bts, nom_proche, norm
from formation_national import ROOT, json_export, reunir_idf

URL=API+'fr-esr-parcoursup/exports/json?'+urllib.parse.urlencode(dict(where='fili="BTS"',select='session,dep,region_etab_aff,acad_mies,cod_uai,g_ea_lib_vx,ville_etab,fil_lib_voe_acc,g_olocalisation_des_formations,capa_fin,voe_tot,acc_tot,acc_bp,lien_form_psup'))


def cle(f,e):
    return f['o'].rsplit('.',1)[-1]+'|'+e['o'].rsplit('.',1)[-1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--academies',nargs='+',required=True)
    p.add_argument('--cache',type=Path,default=Path.home()/'.cache/carte-stages-formation')
    p.add_argument('--revues',type=Path,default=ROOT/'source/formation_parcoursup_revues.json')
    args=p.parse_args();cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    cat=json.loads((ROOT/'commun/academies.json').read_text())
    selected={a['slug'] for a in cat} if args.academies==['toutes'] else set(args.academies)
    if selected-{a['slug'] for a in cat}:p.error('Académie inconnue')
    raw=json_export(URL,cache/'parcoursup-national.json')
    session=max(str(r['session']) for r in raw)
    raw=[r for r in raw if str(r['session'])==session and r.get('g_olocalisation_des_formations')]
    reviews=json.loads(args.revues.read_text()) if args.revues.exists() else []
    reviews={r['onisep']+'|'+str(r['parcoursup']):r for r in reviews}
    regional={};academies={};regions={a['region'] for a in cat if a['slug'] in selected}
    for a in cat:
        if a['slug'] not in selected:continue
        data=json.loads((ROOT/'formation/data'/f"{a['slug']}.json").read_text())
        academies[a['slug']]=data
        dest=regional.setdefault(a['region'],{})
        for f in data['suites'].values():
            if not f['n'].startswith('BTS'):continue
            for e in f['e']:dest[cle(f,e)]=(f,e)
    audit=[];stats=[];accepted={}
    for region in sorted(regions):
        deps={d for a in cat if a['region']==region for d in a['deps']}
        lines=[r for r in raw if str(r['dep']).zfill(2) in deps]
        count=collections.Counter()
        compatible={}
        # Chaque couple diplôme/site n'est compté qu'une fois par région,
        # même quand plusieurs académies utilisent les mêmes lieux de poursuite.
        for key,(f,e) in regional[region].items():
            candidates=[]
            if f['n'] not in compatible:
                compatible[f['n']]=[r for r in lines if meme_bts(f['n'],r['fil_lib_voe_acc'])]
            for r in compatible[f['n']]:
                g=r['g_olocalisation_des_formations'];distance=km(e['lat'],e['lon'],g['lat'],g['lon'])
                if distance<.1 or (distance<2 and nom_proche(e['n'],r['g_ea_lib_vx'],distance)):
                    link=re.search(r'g_ta_cod=(\d+)',r['lien_form_psup'] or '')
                    if link:candidates.append((distance,r,int(link.group(1))))
            unique={g:(d,r,g) for d,r,g in candidates}
            if not unique:count['sans_correspondance']+=1;continue
            if len(unique)>1:
                count['ambigus']+=1
                audit.append(dict(region=region,cle=key,onisep=e['o'],nom=e['n'],formation=f['n'],statut='ambigu',candidats=[dict(nom=r['g_ea_lib_vx'],formation=r['fil_lib_voe_acc'],g=g,distance_m=round(d*1000,1)) for d,r,g in unique.values()]))
                continue
            d,r,g=next(iter(unique.values()))
            different=norm(e['n'])!=norm(r['g_ea_lib_vx'])
            review=reviews.get(e['o']+'|'+str(g))
            ok=not different or (review and review['decision']=='confirme'
                and all(review.get(k)==v for k,v in dict(nom=e['n'],nom_parcoursup=r['g_ea_lib_vx'],formation_parcoursup=r['fil_lib_voe_acc'],uai_parcoursup=r['cod_uai'],distance_m=round(d*1000,1)).items()))
            if different:
                audit.append(dict(region=region,cle=key,onisep=e['o'],nom=e['n'],formation=f['n'],statut='confirme' if ok else 'nom_a_verifier',parcoursup=g,nom_parcoursup=r['g_ea_lib_vx'],formation_parcoursup=r['fil_lib_voe_acc'],uai_parcoursup=r['cod_uai'],ville=r['ville_etab'],distance_m=round(d*1000,1)))
            if not ok:count['noms_non_confirmes']+=1;continue
            vals=[r[k] for k in ['capa_fin','voe_tot','acc_tot','acc_bp']]
            if any(v is None for v in vals):count['chiffres_incomplets']+=1;continue
            x=dict(pl=r['capa_fin'],c=r['voe_tot'],a=r['acc_tot'],bp=r['acc_bp'],g=g)
            if decoupe(f['n'])[1] and decoupe(r['fil_lib_voe_acc'])[1] in ('*',''):x['co']=1
            accepted[key]=x;count['relies']+=1
        total=len(regional[region]);stats.append(dict(region=region,total=total,**dict(count),taux=round(100*count['relies']/total,1) if total else 0))
        print(stats[-1],flush=True)
    files=[]
    for slug,data in academies.items():
        keys={cle(f,e) for f in data['suites'].values() for e in f['e']}
        result={k:v for k,v in accepted.items() if k in keys}
        path=ROOT/'formation/data'/f'{slug}-parcoursup.json'
        path.write_text(json.dumps(dict(session=session,f=result),ensure_ascii=False,separators=(',',':')))
        files.append(dict(slug=slug,relies=len(result),octets=path.stat().st_size,gzip_octets=len(gzip.compress(path.read_bytes(),mtime=0))))
    report=dict(date=datetime.date.today().isoformat(),session=session,source=URL,sha256=hashlib.sha256((cache/'parcoursup-national.json').read_bytes()).hexdigest(),regions=stats,fichiers=files,rapprochements=audit)
    (ROOT/'formation/data/bilan-parcoursup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    reunir_idf()
