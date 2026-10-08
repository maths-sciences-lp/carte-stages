"""Sondage reproductible : stock indépendant + SIRET actuels par département.

Les compteurs de l'API sont des alertes. Les réponses saturées ou discordantes
sont listées, jamais présentées comme une recherche exhaustive actuelle.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time

from stage_collecte import atomic_json
from stage_donnees import preparer
from stage_rattrapage import Rattrapage


def lire(p):return json.loads(p.read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--donnees',type=Path,required=True)
    a=p.parse_args();cache=a.cache
    selection=lire(cache/('sondage-alertes-exclues-100.json' if (cache/'sondage-alertes-exclues-100.json').exists() else 'sondage-exclus-100.json'))
    api=cache/'sondage-api';api.mkdir(exist_ok=True)
    collector=Rattrapage(api,5)
    geography=lire(cache/'communes-reference.json')
    companies={d:lire(cache/'departements'/(d+'.json'))['entreprises'] for d in ('77','93','94')}
    with (cache/'verrou').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        start=time.monotonic();stamp=datetime.now(timezone.utc).isoformat()
        def controle(item):
            dep,siren=item['departement'],item['siren']
            f=api/'entreprises-v2'/dep/(siren+'.json')
            if f.exists():return lire(f)
            # La réponse q=SIREN ne fournit pas la liste publique des sites.
            # Recherche locale par nom puis contrôle exact du SIREN, complétée
            # par le témoin stock et les contrôles individuels de TOUS ses sites.
            result=collector.groupe_communes(dep,companies[dep][siren],[x for x in geography if x.startswith(dep)])
            value=dict(dep=dep,siren=siren,date=datetime.now(timezone.utc).isoformat(),
                       rows=result['rows'],trouve=result['trouve'],
                       sature=result['incertain']=='liste_saturee',
                       incertain=result['incertain'],siret_recus=result.get('siret_recus',[]),
                       discordant=False)
            atomic_json(f,value);return value
        try:
            with ThreadPoolExecutor(max_workers=5) as pool:
                results=list(pool.map(controle,selection['echantillon']))
        finally:
            atomic_json(cache/'executions'/(stamp.replace(':','-')+'.json'),dict(
                phase='sondage_100',debut=stamp,fin=datetime.now(timezone.utc).isoformat(),
                secondes=time.monotonic()-start,requetes=collector.requests,erreurs=dict(collector.errors)))
    stock=lire(cache/'stock-sondage-sites.json')
    inventory={};published={}
    for dep in ('77','93','94'):
        inventory[dep]={r['s'] for r in lire(cache/'departements'/(dep+'.json'))['rows']}
        published[dep]={r[7] for f in (a.donnees/'sirene'/dep).glob('*.json') for r in lire(f)}
    cases=[]
    for result in results:
        dep,siren=result['dep'],result['siren']
        rows={r['s']:r for r in result['rows']}
        # Ajouter tous les sites du stock réinterrogés individuellement, même
        # s'ils n'apparaissent pas dans la liste limitée de la réponse SIREN.
        sites=[x for x in stock if x['dep']==dep and x['siren']==siren]
        for x in sites:
            checked=lire(cache/'stock-api/temoin'/dep/(x['siret']+'.json'))
            rows.update({r['s']:r for r in checked['rows']})
        classified,rejected=preparer(rows.values())
        valid={r[7] for values in classified.values() for r in values}
        case=dict(dep=dep,siren=siren,siret_stock=sorted(x['siret'] for x in sites),
                  siret_admissibles=sorted(valid),absents_inventaire=sorted(valid-inventory[dep]),
                  absents_donnees=sorted(valid-published[dep]),rejets_classement=rejected,
                  liste_saturee=result['sature'],discordance_compteur=result['discordant'],
                  incertain_recherche=result.get('incertain'),
                  entreprise_introuvable=not result['trouve'])
        cases.append(case)
    affected=[x for x in cases if x['absents_inventaire']]
    unresolved=[x for x in cases if x['liste_saturee'] or x['discordance_compteur'] or x['entreprise_introuvable'] or x['incertain_recherche']]
    report=dict(graine=selection['graine'],population=selection['taille_population'],echantillon=len(cases),
                couples_avec_omission=len(affected),taux_omission_mesure=len(affected)/len(cases),
                couples_non_resolus=len(unresolved),cas=cases,
                controle_stock='Tous les SIRET du stock du 1/10 des 100 couples, réinterrogés individuellement',
                limite='Le sondage ne certifie ni la France entière ni les changements non observés après le 1/10.',
                selection_a_elargir=bool(affected))
    atomic_json(cache/'sondage-resultats.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='cas'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
