"""Contrôle indépendant des ajouts locaux du pilote, sans appel à l'API."""
from stage_stock_config import departements
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import re
from urllib.parse import parse_qs

from stage_collecte import ROOT, atomic_json


def lire(path):
    return json.loads(path.read_text())


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def proche(row, point):
    a, b = math.radians(row[3]-point['la']), math.radians(row[4]-point['lo'])
    h = math.sin(a/2)**2 + math.cos(math.radians(row[3]))*math.cos(math.radians(point['la']))*math.sin(b/2)**2
    return 12742*math.asin(math.sqrt(h)) <= 5


def relever_liens(root, cache):
    """Figer formation, UAI, nombres et empreinte des liens avant tout ajout."""
    target=cache/'liens-avant.json'
    if target.exists():
        print('Relevé avant existant conservé'); return
    catalog=lire(root/'catalogue.json')
    forms={f['k']:f for f in catalog['formations']}
    aliases=lire(ROOT/'stage/aliases-idf.json')
    school=next(x for x in lire(ROOT/'data/lycees.json') if x['u']=='0932119Y')
    records=[]
    for name in ['tne','mnb','mama','iccer','mee','tma','era','eeb','geometre','mit','sdg','ebeniste','bma-ebeniste','bma-signaletique','ma','henaff']:
        page=ROOT/name/'index.html';raw=page.read_bytes()
        row=dict(adresse='/'+name+('/' if name=='henaff' else ''),sha256_page=hashlib.sha256(raw).hexdigest())
        if name!='henaff':
            match=re.search(r'location.replace\("[^"#]+#([^"\n]+)"\)',raw.decode())
            if not match:raise ValueError('Redirection inconnue : '+name)
            query=parse_qs(match[1]);key=query['f'][0]
            f=forms[aliases.get(key,key)]
            rows={r[7]:r for dep in ['75','77','78','91','92','93','94','95'] for k in f['s'] for r in lire(root/'sirene'/dep/(k+'.json'))}
            row.update(formation=key,lycee=query['ly'],region=len(rows),cinq_km=sum(proche(r,school) for r in rows.values()))
        records.append(row)
    atomic_json(target,records)


def verifier(root, cache):
    baseline = lire(cache/'ajouts-appliques.json')['base_donnees']
    catalog = lire(root/'catalogue.json')
    changes = sorted(set(git(root, 'diff', '--name-only', baseline).decode().splitlines()
                         +git(root, 'ls-files', '--others', '--exclude-standard').decode().splitlines()))
    oldfiles = set(git(root, 'ls-tree', '-r', '--name-only', baseline).decode().splitlines())
    allowed = {'catalogue.json', 'catalogue-leger.json', 'catalogues/ile-de-france.json',
               'bilan.json', 'tailles-fichiers.csv', 'bilan-academies.csv', 'lba/meta.json',
               'rattrapage-creteil.json', 'rattrapage-idf-complement.json'}
    before_all, after_all, added = set(), set(), set()
    rows_added, preserved, added_lba = 0, 0, 0
    for name in changes:
        parts = name.split('/')
        if parts[0] in ('sirene', 'lba') and len(parts) == 3:
            assert parts[1] in departements(cache), name
            old = json.loads(git(root, 'show', baseline+':'+name)) if name in oldfiles else {}
            new = lire(root/name)
            if parts[0] == 'sirene':
                assert name in oldfiles, name+' : secteur nouveau non prévu'
                assert new[:len(old)] == old, name+' : ligne existante modifiée'
                assert len({r[7] for r in new}) == len(new), name+' : doublon'
                preserved += len(old); rows_added += len(new)-len(old)
                before_all.update(r[7] for r in old); after_all.update(r[7] for r in new)
                added.update(r[7] for r in new[len(old):])
            else:
                assert all(new.get(k) == v for k,v in old.items()), name+' : LBA ancienne modifiée'
                added_lba += len(new.keys()-old.keys())
        elif parts[0] == 'manifestes':
            assert parts[1] in [d+'.json' for d in departements(cache)], name
        else:
            assert name in allowed, name+' : changement hors périmètre'
    assert not before_all-after_all
    hashes = 0
    bydep={d:set() for d in departements(cache)}
    for dep, d in catalog['departements'].items():
        assert lire(root/'manifestes'/(dep+'.json')) == d['secteurs']
        for k, item in d['secteurs'].items():
            path = root/'sirene'/dep/(k+'.json')
            raw = path.read_bytes()
            assert len(raw) == item['bytes'], str(path)
            assert hashlib.sha256(raw).hexdigest() == item['sha256'], str(path)
            if dep in departements(cache):
                values=json.loads(raw)
                assert len(values) == item['n']
                bydep[dep].update(r[7] for r in values)
            hashes += 1
    light = lire(root/'catalogue-leger.json')
    idf = lire(root/'catalogues/ile-de-france.json')
    for cat in (light,idf):
        assert cat['version'] == catalog['version']
        for dep, d in cat['departements'].items():
            assert d['manifeste'] == hashlib.sha256((root/'manifestes'/(dep+'.json')).read_bytes()).hexdigest()
    school = next(l for l in lire(ROOT/'data/lycees.json') if l['u']=='0932119Y')
    forms = {f['k']:f for f in catalog['formations']}
    aliases = lire(ROOT/'stage/aliases-idf.json')
    links = []
    for old in lire(cache/'liens-avant.json'):
        path = ROOT/old['adresse'].strip('/')/'index.html'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == old['sha256_page']
        result = dict(old)
        if 'formation' in old:
            f = forms[aliases.get(old['formation'],old['formation'])]
            rows = {r[7]:r for dep in ('75','77','78','91','92','93','94','95')
                    for k in f['s'] for r in lire(root/'sirene'/dep/(k+'.json'))}
            result['region_apres'] = len(rows)
            result['cinq_km_apres'] = sum(proche(r,school) for r in rows.values())
            assert result['region_apres'] >= old['region']
            assert result['cinq_km_apres'] >= old['cinq_km']
        result['page_inchangee'] = True
        links.append(result)
    declared = lire(cache/'ajouts-appliques.json')
    assert len(added) == declared['ajoutes']
    stock=lire(cache/'stock-bilan.json')
    valid=set(stock['siret_admissibles_et_classes'])
    missing_stock=[x for x in lire(cache/'stock-controles-attendus.json')
                   if x['siret'] in valid and x['siret'] not in bydep[x['dep']]]
    # Une position déjà publiée dans un autre département ne doit jamais être
    # déplacée silencieusement : exposer ces éventuels cas pour la relecture.
    result = dict(ajouts_uniques=len(added),lignes_ajoutees=rows_added,
                  lignes_existantes_preservees_dans_fichiers_modifies=preserved,
                  empreintes_verifiees=hashes,liens=links,
                  lba_lignes_ajoutees=added_lba,
                  octets_sirene=sum(v['bytes'] for d in catalog['departements'].values() for v in d['secteurs'].values()),
                  fichiers_modifies=changes,aucun_retrait=True,aucune_ligne_existante_modifiee=True)
    result['stock_admissibles_encore_absents']=missing_stock
    atomic_json(cache/'verifications-ajouts.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('liens','fichiers_modifies')},ensure_ascii=False))
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--avant',action='store_true')
    args=p.parse_args()
    if args.avant:relever_liens(args.root,args.cache)
    else:verifier(args.root,args.cache)
