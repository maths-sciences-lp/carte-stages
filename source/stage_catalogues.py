"""Catalogues navigateur légers, sans recopier les entreprises.

Le catalogue complet reste le contrat de validation des scripts hors navigateur.
Les manifestes départementaux ne sont lus qu'après le choix d'une formation.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

from stage_collecte import atomic_json

LIMITROPHES = ['02', '10', '27', '28', '45', '51', '60', '89']
IDF = ['75', '77', '78', '91', '92', '93', '94', '95']


def ecrire_catalogues(root):
    root = Path(root)
    full = json.loads((root/'catalogue.json').read_text())
    light = deepcopy(full)
    light['format'] = 'leger-v1'
    for dep, details in light['departements'].items():
        path = root/'manifestes'/f'{dep}.json'
        atomic_json(path, details['secteurs'])
        details.pop('secteurs')
        details['manifeste'] = hashlib.sha256(path.read_bytes()).hexdigest()
    atomic_json(root/'catalogue-leger.json', light)
    names = ['catalogue.json', 'catalogue-leger.json']
    if set(IDF + LIMITROPHES) <= set(light['departements']):
        idf = deepcopy(light)
        idf['departements'] = {dep: idf['departements'][dep] for dep in IDF + LIMITROPHES}
        idf['academies'] = [a for a in idf['academies'] if set(a['deps']) <= set(IDF)]
        for domain in idf['domaines']:
            for sector in domain['s']:
                # Une catégorie peut manquer dans un département (ex. routes de l'État hors de quelques sites).
                sector['c'] = sum(full['departements'][dep]['secteurs'].get(sector['k'], {}).get('n', 0) for dep in IDF)
        atomic_json(root/'catalogues/ile-de-france.json', idf)
        names.append('catalogues/ile-de-france.json')
    else:
        # Un aperçu régional ne doit pas exposer un ancien catalogue IDF complet.
        (root/'catalogues/ile-de-france.json').unlink(missing_ok=True)
    sizes = {}
    for name in names:
        raw = (root/name).read_bytes()
        sizes[name] = {'octets': len(raw), 'gzip': len(gzip.compress(raw, mtime=0))}
    return sizes


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(ecrire_catalogues(args.root), ensure_ascii=False, indent=2))
