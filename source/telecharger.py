import json,subprocess,time,urllib.parse,os,sys
if '--national' in sys.argv:
    sys.argv.remove('--national')
    from stage_collecte import main
    main()
    sys.exit(0)
from domaines import DOMAINES
EMP="01,02,03,11,12,21,22,31,32,41,42,51,52,53"; DEPS=['75','77','78','91','92','93','94','95']
DONE='idf/fait.txt'; OUT='idf/etablissements.jsonl'
done=set(open(DONE).read().split()) if os.path.exists(DONE) else set()
codes=sorted({c for s in DOMAINES.values() for v in s.values() for c in v})
def get(p):
    u='https://recherche-entreprises.api.gouv.fr/search?'+urllib.parse.urlencode(p)
    for k in range(8):
        r=subprocess.run(['curl','-s','-m','30','-A','Mozilla/5.0',u],capture_output=True,text=True).stdout
        try:
            j=json.loads(r)
            if 'results' in j: return j
        except Exception: pass
        time.sleep(min(60,2**k))
    print('ECHEC',p,flush=True); return None
out=open(OUT,'a')
for code in codes:
    for dep in DEPS:
        key=f'{code}|{dep}'
        if key in done: continue
        page=1; n=0; ok=True
        while True:
            j=get(dict(activite_principale=code,departement=dep,etat_administratif='A',tranche_effectif_salarie=EMP,per_page=25,page=page,limite_matching_etablissements=100))
            if j is None: ok=False; break
            for h in j['results']:
                for e in h.get('matching_etablissements') or []:
                    if e.get('etat_administratif')!='A' or not str(e.get('code_postal','')).startswith(dep): continue
                    out.write(json.dumps(dict(s=e['siret'],n=h['nom_complet'],e=', '.join(e.get('liste_enseignes') or []),
                        c=e.get('activite_principale') or code,q=code,ad=e.get('adresse'),la=e.get('latitude'),lo=e.get('longitude'),
                        t=h.get('tranche_effectif_salarie'),nj=h.get('nature_juridique'),du=h.get('statut_diffusion'),de=e.get('statut_diffusion_etablissement'),
                        r=bool(e.get('liste_rge'))),ensure_ascii=False)+'\n'); n+=1
            tp=j.get('total_pages',0)
            if page>=tp: break
            if page>=400: print('LIMITE 10000',key,flush=True); break
            page+=1; time.sleep(0.12)
        out.flush()
        if ok:
            open(DONE,'a').write(key+'\n'); done.add(key)
        print(key,n,flush=True)
print('FINI',flush=True)
