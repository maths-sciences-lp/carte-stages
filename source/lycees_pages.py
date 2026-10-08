"""Page « Mon lycée » (/lycee/) : les formations de chaque lycée de France, avec ses liens.

Pour chaque lycée qui prépare un CAP, un bac pro, un BMA ou une 2de pro (Onisep, même
fichier que les autres outils) :
- « Mon stage » : carte de Trouve ton stage avec la formation et le lycée déjà choisis,
  quand la formation a sa carte (catalogue de carte-stages-donnees) ;
- « Après mon diplôme » : Après le lycée avec le diplôme et le lycée déjà choisis,
  quand le diplôme y figure (fichiers formation/data/<académie>.json).

Sorties : lycee/data/index.json (recherche : UAI, nom, commune, académie) et
lycee/data/<académie>.json (formations de chaque lycée).

python3 source/lycees_pages.py --sources DOSSIER --catalogue /copie/carte-stages-donnees/catalogue-leger.json
"""
import argparse
import collections
import csv
import gzip
import json
import math
from pathlib import Path
import re

from stage_donnees import slug

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'lycee/data'
TYPES = {'CAP': 'CAP', 'CAP agricole': 'CAP agricole', 'baccalauréat professionnel': 'Bac pro',
         "brevet des métiers d'art": 'BMA', 'classe de 2de professionnelle': '2de pro'}
# Familles de métiers de 2de pro → carte de stage (catalogue « 2nde pro »).
SECONDES = {
    'relation client': '2nde-relation-client-mrc',
    'transitions numérique et énergétique': '2nde-transitions-numerique-et-energetique-tne',
    'gestion administrative, du transport et de la logistique': '2nde-gestion-administrative-transport-et-logistique-gatl',
    "pilotage et de la maintenance d'installations automatisées": '2nde-pilotage-et-maintenance-d-installations-automatisees-pm',
    "réalisation d'ensembles mécaniques et industriels": '2nde-realisation-d-ensembles-mecaniques-et-industriels-mremi',
    'maintenance des matériels et des véhicules': '2nde-maintenance-des-materiels-et-des-vehicules',
    'hôtellerie-restauration': '2nde-hotellerie-restauration',
    'construction durable, du bâtiment et des travaux publics': '2nde-construction-durable-batiment-et-travaux-publics',
    "agencement, de la menuiserie et de l'ameublement": '2nde-agencement-menuiserie-et-ameublement-mama',
    'études et de la modélisation numérique du bâtiment': '2nde-etudes-et-modelisation-numerique-du-batiment-emnb',
    'beauté et du bien-être': '2nde-beaute-et-bien-etre',
    'alimentation': '2nde-alimentation',
    'industries graphiques et de la communication': '2nde-industries-graphiques-et-communication',
    'aéronautique': '2nde-aeronautique',
}


def famille(lib):
    m = re.match(r"classe de 2de professionnelle métiers (?:de la |de l'|des |du |de )?(.*)$", lib)
    return SECONDES.get(m.group(1)) if m else None


def nom(lib):
    lib = re.sub(r'^classe de 2de professionnelle ', '2de pro ', lib)
    lib = re.sub(r'^CAPa ', 'CAP agricole ', lib)
    return lib[:1].upper() + lib[1:]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True, help='Dossier du CSV Onisep 605340ddc19a9.csv')
    p.add_argument('--catalogue', type=Path, required=True)
    args = p.parse_args()
    catalog = json.loads((ROOT/'commun/academies.json').read_text())
    nom_ac = {re.sub(r"^Académie (?:de |d')", '', a['nom']): a['slug'] for a in catalog}
    cles = {f['k'] for f in json.loads(args.catalogue.read_text())['formations']}
    alias = json.loads((ROOT/'stage/aliases-idf.json').read_text())

    def carte(lib):
        if lib.startswith('classe de 2de professionnelle'):
            k = famille(lib)
            return k if k in cles else ''
        l = lib.replace('CAP agricole ', 'CAPa ').replace("brevet des métiers d'art ", 'BMA ').replace('Brevet des métiers d’art ', 'BMA ')
        # Identifiants longs, variante sans lettre d'option, et anciens identifiants coupés à 60 caractères.
        for k in (slug(l, 200), re.sub(r'-option-[a-e]-', '-option-', slug(l, 200)), slug(l, 60)):
            k = alias.get(k, k)
            if k in cles:
                return k
        return ''

    # Diplômes et lycées connus d'Après le lycée, par académie (#d=…&ly=…).
    apres = {}
    for a in catalog:
        d = json.loads((ROOT/'formation/data'/f"{a['slug']}.json").read_text())
        apres[a['slug']] = {(i, u) for i, x in d['dip'].items() for u in x['ly']}

    lycees = collections.defaultdict(dict)
    with (args.sources/'605340ddc19a9.csv').open(encoding='utf-8-sig') as f:
        for r in csv.DictReader(f, delimiter=';'):
            t = TYPES.get(r['FOR type'])
            s = nom_ac.get(r['ENS académie'])
            u = r['ENS code UAI']
            if not t or not s or not u or r['ENS commune'] == 'Monaco':
                continue
            try:
                lat, lon = float(r['ENS latitude']), float(r['ENS longitude'])
                if not (math.isfinite(lat) and math.isfinite(lon)) or (lat, lon) == (0, 0):
                    continue
            except ValueError:
                continue
            ly = lycees[s].setdefault(u, dict(n=r["Lieu d'enseignement (ENS) libellé"], v=r['ENS commune'], f={}))
            lib = r['Formation (FOR) libellé']
            fid = r['FOR URL et ID Onisep'].rsplit('.', 1)[-1]
            if lib not in ly['f']:
                ly['f'][lib] = [t, nom(lib), fid, carte(lib), fid if (fid, u) in apres[s] else '']
    rang = {'2de pro': 0, 'Bac pro': 1, 'CAP': 2, 'CAP agricole': 3, 'BMA': 4}
    OUT.mkdir(parents=True, exist_ok=True)
    index, bilan = [], dict(lycees=0, formations=0, avec_carte=0, avec_apres=0, academies={})
    for s in sorted(lycees):
        data = {}
        for u, ly in sorted(lycees[s].items(), key=lambda x: (x[1]['n'], x[1]['v'])):
            fs = sorted(ly['f'].values(), key=lambda x: (rang[x[0]], x[1]))
            data[u] = dict(n=ly['n'], v=ly['v'], f=fs)
            index.append([u, ly['n'], ly['v'], s])
            bilan['formations'] += len(fs)
            bilan['avec_carte'] += sum(1 for x in fs if x[3])
            bilan['avec_apres'] += sum(1 for x in fs if x[4])
        path = OUT/f'{s}.json'
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
        bilan['academies'][s] = dict(lycees=len(data), octets_gzip=len(gzip.compress(path.read_bytes(), mtime=0)))
    bilan['lycees'] = len(index)
    path = OUT/'index.json'
    path.write_text(json.dumps(index, ensure_ascii=False, separators=(',', ':')))
    bilan['index_octets_gzip'] = len(gzip.compress(path.read_bytes(), mtime=0))
    (OUT/'bilan.json').write_text(json.dumps(bilan, ensure_ascii=False, indent=2)+'\n')
    print({k: v for k, v in bilan.items() if k != 'academies'})


if __name__ == '__main__':
    main()
