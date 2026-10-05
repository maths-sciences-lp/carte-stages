import json,subprocess,time,urllib.parse,sys
EMP="01,02,03,11,12,21,22,31,32,41,42,51,52,53"
NAF={'43.22A':'Énergie','43.22B':'Énergie','35.30Z':'Énergie','43.32A':'Menuiserie-agencement','16.23Z':'Menuiserie-agencement',
 '31.09B':'Ébénisterie','95.24Z':'Ébénisterie','31.01Z':'Ébénisterie','18.12Z':'Signalétique-graphisme','18.13Z':'Signalétique-graphisme',
 '71.12A':'Géomètre-topographe','74.90A':'Bâtiment-études','71.12B':"Bureaux d'études techniques"}
KW={'signaletique':'Signalétique-graphisme','enseignes':'Signalétique-graphisme','serigraphie':'Signalétique-graphisme','marquage publicitaire':'Signalétique-graphisme',
 'ebeniste':'Ébénisterie','ebenisterie':'Ébénisterie','agencement':'Menuiserie-agencement','menuiserie':'Menuiserie-agencement','agenceur':'Menuiserie-agencement',
 'geometre':'Géomètre-topographe','topographie':'Géomètre-topographe','economiste construction':'Bâtiment-études','genie climatique':'Énergie','pompe a chaleur':'Énergie'}
def get(p):
    u='https://recherche-entreprises.api.gouv.fr/search?'+urllib.parse.urlencode(p)
    for k in range(6):
        out=subprocess.run(['curl','-s','-A','Mozilla/5.0',u],capture_output=True,text=True).stdout
        try:
            j=json.loads(out)
            if 'results' in j: return j
        except Exception: pass
        time.sleep(1.5*(k+1))
    print('ECHEC',p,file=sys.stderr); return {'results':[],'total_pages':0}
rows={}
def run(base,fil,how,maxp=400):
    for dep in ('75','93'):
        page=1
        while True:
            j=get(dict(base,departement=dep,etat_administratif='A',tranche_effectif_salarie=EMP,per_page=25,page=page))
            for h in j['results']:
                for e in h.get('matching_etablissements') or []:
                    if e.get('etat_administratif')!='A' or not str(e.get('code_postal','')).startswith(dep) or e['siret'] in rows: continue
                    rows[e['siret']]=dict(siret=e['siret'],siren=h['siren'],nom=h['nom_complet'],ens=', '.join(e.get('liste_enseignes') or []),
                        naf=e.get('activite_principale') or h.get('activite_principale'),fil=fil,how=how,adr=e.get('adresse'),cp=e.get('code_postal'),ville=e.get('libelle_commune'),
                        la=e.get('latitude'),lo=e.get('longitude'),eff=h.get('tranche_effectif_salarie'),crea=h.get('date_creation'),
                        nj=h.get('nature_juridique'),diff_ul=h.get('statut_diffusion'),diff_et=e.get('statut_diffusion_etablissement'),rge=bool(e.get('liste_rge')))
            if page>=min(j.get('total_pages',0),maxp): break
            page+=1; time.sleep(0.16)
    print(how,fil,len(rows),flush=True)
for naf,fil in NAF.items(): run({'activite_principale':naf},fil,'naf '+naf)
for kw,fil in KW.items(): run({'q':kw,'section_activite_principale':'C,F,M'},fil,'mot '+kw,maxp=20)
json.dump(list(rows.values()),open('prospects.json','w'),ensure_ascii=False)
