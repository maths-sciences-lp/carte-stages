"""Vérification ciblée des SIRET absents ; jamais une nouvelle collecte nationale.

--root-donnees /copie/donnees --sortie /tmp/entreprises-api.json
Deux appels par seconde au plus, reprise locale et temporisation après HTTP 429.
Ne stocke ni noms, ni contacts, ni réponses brutes ; seulement la preuve d'état.
"""
import argparse,json,time,urllib.request,urllib.error,urllib.parse
from datetime import datetime,timezone
from pathlib import Path
from stage_collecte import atomic_json,ROOT
from verif_stage_comptages import comparer

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-donnees',type=Path,required=True);p.add_argument('--sortie',type=Path,required=True);a=p.parse_args()
    rows=comparer(ROOT,a.root_donnees)
    sirets=sorted({e['siret'] for r in rows for e in r['details'] if not e['secteurs_apres']})
    proof=json.loads(a.sortie.read_text()) if a.sortie.exists() else {}
    for s in sirets:
        if s in proof and 'resultat' in proof[s]:continue
        url='https://recherche-entreprises.api.gouv.fr/search?'+urllib.parse.urlencode({'q':s,'per_page':1})
        for attempt in range(6):
            try:
                data=json.load(urllib.request.urlopen(url,timeout=30));break
            except urllib.error.HTTPError as e:
                if e.code!=429 or attempt==5:raise
                time.sleep(max(30,float(e.headers.get('Retry-After') or 30)))
        found=[]
        for h in data.get('results',[]):
            for e in [h.get('siege',{})]+h.get('matching_etablissements',[]):
                if e.get('siret')==s:
                    found.append(dict(siret=s,etat=e.get('etat_administratif'),naf=e.get('activite_principale'),lat=e.get('latitude'),lon=e.get('longitude'),diffusion=e.get('statut_diffusion_etablissement'),nature=h.get('nature_juridique'),effectif=h.get('tranche_effectif_salarie'),naf_unite=h.get('activite_principale')))
        proof[s]={'date':datetime.now(timezone.utc).date().isoformat(),'url':url,'resultat':found[:1]}
        atomic_json(a.sortie,proof);time.sleep(.5)
    print(f'{len(sirets)} SIRET documentés dans {a.sortie}')
if __name__=='__main__':main()
