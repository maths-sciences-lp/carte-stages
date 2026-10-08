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
    idf = deepcopy(light)
    idf['departements'] = {dep: idf['departements'][dep] for dep in IDF + LIMITROPHES}
    idf['academies'] = [a for a in idf['academies'] if set(a['deps']) <= set(IDF)]
    for domain in idf['domaines']:
        for sector in domain['s']:
            sector['c'] = sum(full['departements'][dep]['secteurs'][sector['k']]['n'] for dep in IDF)
    atomic_json(root/'catalogues/ile-de-france.json', idf)
    sizes = {}
    for name in ['catalogue.json', 'catalogue-leger.json', 'catalogues/ile-de-france.json']:
        raw = (root/name).read_bytes()
        sizes[name] = {'octets': len(raw), 'gzip': len(gzip.compress(raw, mtime=0))}
    return sizes


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(ecrire_catalogues(args.root), ensure_ascii=False, indent=2))
