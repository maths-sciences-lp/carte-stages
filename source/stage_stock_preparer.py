"""Prépare les écarts, le témoin historique et le sondage sans refaire l'inventaire API.

La sélection compare les SIRET du stock par (SIREN, département). Les compteurs
ne servent qu'à repérer des entreprises multisites, jamais à expliquer un écart.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import shutil

from stage_collecte import ROOT, CODES, EFFECTIFS, atomic_json
from stage_rattrapage import temoin
from stage_stock_config import departements, extrait, espace_libre
from stage_stock_comparer import creer_diagnostic


def lire(path): return json.loads(path.read_text())


def selectionner(candidates, published, multisites, count, seed):
    population=[]
    for (dep,siren),sites in sorted(candidates.items()):
        if len(sites)>1 or siren in multisites:
            # Une entreprise n'est écartée que si chaque SIRET candidat du stock
            # est déjà présent dans ce département. Pas de compensation ailleurs.
            if sites <= published[dep]:
                population.append(dict(departement=dep,siren=siren,siret_recus=sorted(sites)))
    if len(population)<count: raise ValueError('Population insuffisante pour le sondage')
    return population, random.Random(seed).sample(population,count)


def main():
    import duckdb
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--cache-national',type=Path,required=True)
    p.add_argument('--donnees',type=Path,required=True)
    p.add_argument('--communes',type=Path,required=True)
    p.add_argument('--graine',type=int,required=True)
    a=p.parse_args();cache=a.cache;deps=departements(cache);espace_libre(cache)
    if (cache/'ajouts-appliques.json').exists():
        print('Sélection et sondage initiaux conservés après application des ajouts'); return
    c=duckdb.connect();c.execute("SET memory_limit='384MB'");c.execute('SET threads=2')
    for phase,table in [('etablissements','e'),('unites','u')]:
        f=extrait(cache,phase)
        if hashlib.sha256(f.read_bytes()).hexdigest()!=lire(cache/('stock-'+phase+'-provenance.json'))['sha256']:
            raise ValueError('Empreinte incorrecte')
        c.from_parquet(str(f)).create_view(table)
    c.execute('CREATE TABLE codes AS SELECT unnest(?) AS code',[CODES])
    c.execute('CREATE TABLE effectifs AS SELECT unnest(?) AS code',[EFFECTIFS])
    creer_diagnostic(c)
    published={d:{r[7] for f in (a.donnees/'sirene'/d).glob('*.json') for r in lire(f)} for d in deps}
    candidates=defaultdict(set)
    for s,sir,commune in c.execute("SELECT siret,siren,codeCommuneEtablissement FROM diagnostic WHERE motif='candidat' ORDER BY siret").fetchall():
        dep=commune[:3] if commune.startswith(('97','98')) else commune[:2]
        candidates[dep,sir].add(s)
    # Cache ancien = indice multisite seulement ; tous les sites explicatifs
    # des couples sondés seront revérifiés individuellement aujourd'hui.
    totals=Counter()
    for f in sorted((a.cache_national/'departements').glob('*.json')):
        for r in lire(f)['rows']:totals[r['s'][:9]]+=1
    population,sample=selectionner(candidates,published,{s for s,n in totals.items() if n>1},100,a.graine)
    target=cache/'sondage-alertes-exclues-100.json'
    selection=dict(graine=a.graine,taille_population=len(population),echantillon=sample,
        definition='Entreprises multisites observées dans le cache national ou le stock local ; tous leurs SIRET admissibles du stock sont déjà présents dans le même département.',
        limite='Stock daté ; le sondage recherche aussi des changements récents par nom et communes et vérifie chaque SIRET explicatif.')
    if target.exists() and lire(target)!=selection:raise ValueError('Le sondage existant ne doit pas changer silencieusement')
    atomic_json(target,selection)
    atomic_json(cache/'sondage-exclus-100.json',dict(echantillon=[]))
    atomic_json(cache/'sondage-population.json',population)
    for dep in deps:
        rows=lire(a.cache_national/'departements'/(dep+'.json'))['rows']
        selected={x['siren'] for x in sample if x['departement']==dep}
        companies={};kept=[]
        for r in rows:
            sir=r['s'][:9]
            if sir in selected:
                companies[sir]=dict(siren=sir,nom=r['n'],naf=r['q'],effectif=r['t'],liste_saturee=False)
                kept.append(r)
        if selected-companies.keys():raise ValueError('Entreprise du sondage absente du cache descriptif')
        atomic_json(cache/'departements'/(dep+'.json'),dict(rows=kept,entreprises=companies,
            usage='Descriptions historiques pour requêtes de contrôle ; jamais utilisées comme ajouts sans vérification individuelle'))
    geo=lire(a.communes)
    # Paris : les 20 arrondissements sont interrogés, pas le code générique.
    if '75' in deps:geo=sorted((set(geo)-{'75056'})|{str(75100+i) for i in range(1,21)})
    atomic_json(cache/'communes-reference.json',geo)
    atomic_json(cache/'temoin-attendu.json',temoin(ROOT,a.donnees,deps))
    atomic_json(cache/'cibles.json',{d:dict(cibles_siren=[]) for d in deps})
    print(json.dumps(dict(departements=deps,population=len(population),sondage=Counter(x['departement'] for x in sample),
                         temoins={d:len(v) for d,v in lire(cache/'temoin-attendu.json').items()}),ensure_ascii=False))


if __name__=='__main__': main()
