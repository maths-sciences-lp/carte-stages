"""Compare le témoin Insee Créteil aux SIRET publiés, puis prépare les contrôles.

Le stock au 1/10 est un témoin indépendant daté, pas une preuve de l'état au
8/10. Les candidats sont toujours revérifiés par SIRET avant tout ajout.
"""
from stage_stock_config import configuration, departements, extrait, espace_libre
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from stage_collecte import CODES, EFFECTIFS, atomic_json


def lire(p):
    return json.loads(p.read_text())


def creer_diagnostic(c):
    c.execute("""CREATE VIEW diagnostic AS SELECT e.*,u.* EXCLUDE(siren),
      CASE WHEN u.siren IS NULL THEN 'unite_absente'
       WHEN u.etatAdministratifUniteLegale != 'A' OR u.etatAdministratifUniteLegale IS NULL THEN 'unite_non_active'
       WHEN u.activitePrincipaleUniteLegale NOT IN (SELECT code FROM codes) OR u.activitePrincipaleUniteLegale IS NULL THEN 'naf_unite_hors_liste'
       WHEN u.trancheEffectifsUniteLegale NOT IN (SELECT code FROM effectifs) OR u.trancheEffectifsUniteLegale IS NULL THEN 'effectif_hors_liste'
       WHEN u.categorieJuridiqueUniteLegale = '1000' THEN 'entrepreneur_individuel'
       WHEN u.statutDiffusionUniteLegale IS DISTINCT FROM 'O' OR e.statutDiffusionEtablissement IS DISTINCT FROM 'O' THEN 'non_diffusible'
       WHEN e.etatAdministratifEtablissement IS DISTINCT FROM 'A' THEN 'ferme'
       ELSE 'candidat' END AS motif
      FROM e LEFT JOIN u USING(siren)""")


def main():
    import duckdb
    from pyproj import Transformer
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--donnees', type=Path, required=True)
    a = p.parse_args()
    cache=a.cache
    if (cache/'ajouts-appliques.json').exists():
        print('Comparaison initiale conservée après application des ajouts'); return
    espace_libre(cache)
    c = duckdb.connect()
    c.execute("SET memory_limit='384MB'")
    for phase, table in [('etablissements','e'),('unites','u')]:
        f = extrait(cache,phase)
        provenance = lire(a.cache/('stock-'+phase+'-provenance.json'))
        if hashlib.sha256(f.read_bytes()).hexdigest() != provenance['sha256']:
            raise ValueError('Empreinte invalide : '+phase)
        c.from_parquet(str(f)).create_view(table)
    c.execute('CREATE TABLE codes AS SELECT unnest(?) AS code',[CODES])
    c.execute('CREATE TABLE effectifs AS SELECT unnest(?) AS code',[EFFECTIFS])
    # L'API filtre l'activité ET l'effectif de l'unité légale. Ne pas filtrer
    # uniquement le NAF établissement : cela perdrait des sites admissibles.
    creer_diagnostic(c)
    stats = c.execute("SELECT CASE WHEN starts_with(codeCommuneEtablissement,'97') OR starts_with(codeCommuneEtablissement,'98') THEN substr(codeCommuneEtablissement,1,3) ELSE substr(codeCommuneEtablissement,1,2) END,motif,count(*) FROM diagnostic GROUP BY ALL ORDER BY ALL").fetchall()
    report = {'stock':configuration(cache)['date_stock'],'perimetre':departements(cache), 'departements':{},
              'limite':'État du stock au 1/10, différent de la collecte du 8/10 ; candidats vérifiés individuellement avant ajout.'}
    existing = {}; current = {}
    for dep in departements(cache):
        existing[dep] = {r[7] for f in (a.donnees/'sirene'/dep).glob('*.json') for r in lire(f)}
        current[dep] = {r['s']:r for r in lire(a.cache/'departements'/(dep+'.json'))['rows']}
        for f in sorted((a.cache/'temoin'/dep).glob('*.json')):
            current[dep].update({r['s']:r for r in lire(f)['rows']})
        report['departements'][dep] = {'repartition_stock':{reason:n for d,reason,n in stats if d==dep}}
    rows = c.execute("""SELECT siret,siren,CASE WHEN starts_with(codeCommuneEtablissement,'97') OR starts_with(codeCommuneEtablissement,'98') THEN substr(codeCommuneEtablissement,1,3) ELSE substr(codeCommuneEtablissement,1,2) END,
        coordonneeLambertAbscisseEtablissement,coordonneeLambertOrdonneeEtablissement,
        nomenclatureActivitePrincipaleEtablissement,nomenclatureActivitePrincipaleUniteLegale
        FROM diagnostic WHERE motif='candidat' ORDER BY siret""").fetchall()
    transformer = Transformer.from_crs('EPSG:2154','EPSG:4326',always_xy=True)
    todo = []; positions = []; bydep = {d:Counter() for d in existing}; expected = {d:[] for d in existing}
    for s,siren,dep,x,y,ne,nu in rows:
        expected[dep].append(s)
        bydep[dep]['candidats'] += 1
        if nu != 'NAFRev2' or ne not in ('NAFRev2',None):
            raise ValueError('Nomenclature inattendue pour '+s)
        try:
            lon,lat = transformer.transform(float(x),float(y),errcheck=True)
            if not (math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180) or (lat,lon)==(0,0):
                raise ValueError()
        except (ValueError,TypeError):
            lon=lat=None; bydep[dep]['sans_coordonnees_stock']+=1
        if s in existing[dep]: bydep[dep]['deja_presents'] += 1
        else:
            todo.append({'dep':dep,'siret':s,'source':'stock_'+configuration(cache)['date_stock']})
            bydep[dep]['absents_donnees'] += 1
        if len([v for v in positions if v['dep']==dep])<10 and s in current[dep] and lat is not None:
            api=current[dep][s]
            phi1,phi2=map(math.radians,[lat,api['la']]); dl=math.radians(lon-api['lo']);dp=phi1-phi2
            distance=2*6371000*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2)))
            positions.append({'siret':s,'dep':dep,'stock':[lat,lon],'api':[api['la'],api['lo']],'ecart_metres':round(distance,2)})
    for dep in bydep: report['departements'][dep].update(bydep[dep])
    report['controle_coordonnees']=positions
    report['ecarts_coordonnees_superieurs_50m']=[v for v in positions if v['ecart_metres']>=50]
    # Tous les sites du stock des 100 couples sont comparés, pas leurs comptes.
    sample=lire(a.cache/'sondage-exclus-100.json')
    if (a.cache/'sondage-alertes-exclues-100.json').exists():
        sample['echantillon']+=lire(a.cache/'sondage-alertes-exclues-100.json')['echantillon']
    c.execute('CREATE TABLE sondage(dep VARCHAR,siren VARCHAR)')
    c.executemany('INSERT INTO sondage VALUES (?,?)',sorted({(x['departement'],x['siren']) for x in sample['echantillon']}))
    sample_rows=c.execute("""SELECT d.siret,d.siren,s.dep,d.motif FROM diagnostic d JOIN sondage s
       ON d.siren=s.siren AND CASE WHEN starts_with(d.codeCommuneEtablissement,'97') OR starts_with(d.codeCommuneEtablissement,'98') THEN substr(d.codeCommuneEtablissement,1,3) ELSE substr(d.codeCommuneEtablissement,1,2) END=s.dep ORDER BY d.siret""").fetchall()
    atomic_json(a.cache/'stock-sondage-sites.json',[dict(siret=s,siren=sir,dep=d,motif=m) for s,sir,d,m in sample_rows])
    atomic_json(a.cache/'stock-candidats-attendus.json',expected)
    atomic_json(a.cache/'stock-controles-attendus.json',todo)
    atomic_json(a.cache/'stock-comparaison.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
