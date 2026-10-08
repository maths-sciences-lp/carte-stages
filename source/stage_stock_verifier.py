"""Contrôle individuel reprenable des écarts au stock et du sondage Créteil."""
from stage_stock_config import configuration, departements, extrait, espace_libre
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time

from stage_collecte import atomic_json
from stage_rattrapage import Rattrapage


def lire(p):
    return json.loads(p.read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--cache-national',type=Path,required=True)
    a=p.parse_args(); cache=a.cache
    expected=lire(cache/'stock-controles-attendus.json')
    tasks={(x['dep'],x['siret']) for x in expected}
    sample=lire(cache/'sondage-exclus-100.json')
    if (cache/'sondage-alertes-exclues-100.json').exists():
        sample['echantillon']+=lire(cache/'sondage-alertes-exclues-100.json')['echantillon']
    pairs={(x['departement'],x['siren']) for x in sample['echantillon']}
    # Recontrôler tous les sites du stock pour les couples sondés, même fermés
    # au 1/10 : des réouvertures peuvent avoir eu lieu avant notre contrôle.
    sample_tasks={(x['dep'],x['siret']) for x in lire(cache/'stock-sondage-sites.json')}
    # L'ancien cache ne sert jamais d'explication par un simple compteur.
    # Vérifier ses identifiants exacts dans le département concerné.
    explanation=set()
    for dep in departements(cache):
        for row in lire(a.cache_national/'departements'/(dep+'.json'))['rows']:
            if (dep,row['s'][:9]) in pairs:explanation.add((dep,row['s']))
        for x in sample['echantillon']:
            if x['departement']==dep:
                sample_tasks.update((dep,s) for s in x['siret_recus'])
    historical=lire(cache/'temoin-attendu.json')
    tasks.update((d,s) for d,sites in historical.items() for s in sites)
    tasks.update(sample_tasks|explanation)
    atomic_json(cache/'stock-verifications-attendues.json',dict(
        controles=[dict(dep=d,siret=s) for d,s in sorted(tasks)],
        sondage=[dict(dep=d,siret=s) for d,s in sorted(sample_tasks)],
        explications_cache=[dict(dep=d,siret=s) for d,s in sorted(explanation)]))
    api=cache/'stock-api';api.mkdir(exist_ok=True)
    with (cache/'verrou').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Les vérifications historiques déjà faites dans ce cache daté restent conservées.
        # Ne pas réécrire le cache d'origine ni refaire ces appels.
        for dep,s in tasks:
            old=cache/'temoin'/dep/(s+'.json');new=api/'temoin'/dep/(s+'.json')
            if old.exists() and not new.exists():atomic_json(new,lire(old))
        collector=Rattrapage(api,5)
        start=time.monotonic();stamp=datetime.now(timezone.utc).isoformat()
        print(f'CONTROLES INDIVIDUELS : {len(tasks)} SIRET, dont {len(sample_tasks)} pour le sondage et {len(explanation)} cache explicatif',flush=True)
        try:
            with ThreadPoolExecutor(max_workers=5) as pool:
                for i,value in enumerate(pool.map(collector.verifier_siret,sorted(tasks)),1):
                    if i%100==0:print(f'VERIFIES : {i}/{len(tasks)} ; requêtes nouvelles {collector.requests}',flush=True)
        finally:
            record=dict(phase='stock_controles',debut=stamp,fin=datetime.now(timezone.utc).isoformat(),
                        secondes=time.monotonic()-start,requetes=collector.requests,erreurs=dict(collector.errors))
            atomic_json(cache/'executions'/(stamp.replace(':','-')+'.json'),record)
            print(json.dumps(record,ensure_ascii=False),flush=True)
        for d,sites in historical.items():
            for s in sites:
                atomic_json(cache/'temoin'/d/(s+'.json'),lire(api/'temoin'/d/(s+'.json')))
        missing=[(d,s) for d,s in tasks if not (api/'temoin'/d/(s+'.json')).exists()]
        if missing:raise RuntimeError('Contrôles encore manquants')
        counts={d:Counter() for d in departements(cache)}
        for x in expected:
            v=lire(api/'temoin'/x['dep']/(x['siret']+'.json'))
            if v['rows']:counts[x['dep']]['admissibles']+=1
            else:counts[x['dep']].update(v['rejets'])
        atomic_json(cache/'stock-verification-resultats.json',dict(
            terminee=True,attendus=len(tasks),ecarts_stock={d:dict(v) for d,v in counts.items()},
            limite='Un rejet actuel ne prouve pas sa date de survenue entre le stock et le contrôle API.'))
        print(json.dumps({d:dict(v) for d,v in counts.items()},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
