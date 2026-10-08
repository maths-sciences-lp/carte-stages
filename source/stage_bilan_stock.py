"""Preuves du pilote : un statut par écart SIRET et limites explicites."""
from stage_stock_config import configuration, departements, extrait, espace_libre
import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from stage_collecte import atomic_json
from stage_donnees import preparer


def lire(p):return json.loads(p.read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    a=p.parse_args();cache=a.cache
    if not lire(cache/'stock-verification-resultats.json')['terminee']:
        raise RuntimeError('Contrôles du stock incomplets')
    expected=lire(cache/'stock-controles-attendus.json')
    checked={x['siret']:lire(cache/'stock-api/temoin'/x['dep']/(x['siret']+'.json')) for x in expected}
    rows={r['s']:r for x in checked.values() for r in x['rows']}
    grouped,_=preparer(rows.values())
    valid={r[7] for group in grouped.values() for r in group}
    statuses=[];counts={d:Counter() for d in departements(cache)}
    for x in expected:
        s,dep=x['siret'],x['dep'];v=checked[s]
        if s in valid:
            status='admissible_et_classe';motif=''
        elif not v['rows']:
            status='rejete_au_controle_actuel';motif=';'.join(sorted(v['rejets']))
        else:
            status='rejete_au_classement';motif=';'.join(sorted(preparer(v['rows'])[1]))
        counts[dep][status]+=1
        statuses.append(dict(departement=dep,siret=s,statut=status,motif=motif,
                             controle_le=v['date'],nom=rows.get(s,{}).get('n','')))
    with (cache/'stock-ecarts-expliques.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(statuses[0]),lineterminator='\n');w.writeheader();w.writerows(statuses)
    saturated=[];remaining=[]
    initial=lire(cache/'cibles.json')
    for dep in departements(cache):
        for siren,c in lire(cache/'departements'/(dep+'.json'))['entreprises'].items():
            if c['liste_saturee']:saturated.append(dict(dep=dep,siren=siren,nom=c.get('nom')))
        for siren in initial[dep]['cibles_siren']:
            f=cache/'entreprises'/dep/(siren+'.json')
            if not f.exists():remaining.append(dict(dep=dep,siren=siren,motif='recherche_geographique_remplacee_par_stock_date'))
            else:
                for item in lire(f)['incertains']:remaining.append(dict(dep=dep,siren=siren,**item))
    coord=lire(cache/'stock-comparaison.json')
    summary=dict(stock=configuration(cache)['date_stock'],ecarts=len(expected),statuts=len(statuses),
                 sans_statut=0,par_departement={d:dict(v) for d,v in counts.items()},
                 siret_admissibles_et_classes=sorted(valid),
                 listes_initiales_saturees=len(saturated),couples_geographiques_non_certifies=len(remaining),
                 limite_temporelle='Le stock daté du '+configuration(cache)['date_stock']+' ne prouve pas l’exhaustivité à la date de contrôle API. Les écarts de dates sont séparés des pertes ; aucune date de fermeture n’est déduite sans preuve.',
                 limite_coordonnees=f"Positions API conservées. {len(coord['ecarts_coordonnees_superieurs_50m'])} des {len(coord['controle_coordonnees'])} comparaisons Lambert93/WGS84 dépassent 50 m ; aucune substitution automatique.",
                 preuve='Chaque SIRET candidat du stock absent des données possède un contrôle individuel et un statut. Les autres sites du stock sont déjà présents.')
    atomic_json(cache/'stock-bilan.json',summary)
    atomic_json(cache/'listes-saturees-et-limites.json',dict(listes_saturees=saturated,couples_non_certifies=remaining))
    print(json.dumps({k:v for k,v in summary.items() if k!='siret_admissibles_et_classes'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
