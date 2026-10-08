"""Qui peut m'aider ? : chaque lieu est dans le département de son académie (contour officiel,
à 3 km près), comme les collèges et lycées proposés comme points de départ."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'source'))
from apres3e_voisins import dedans, distance_km, segments  # noqa: E402

catalog = json.loads((ROOT/'commun/academies.json').read_text())
SEG = {}


def dans(lat, lon, deps):
    for d in deps:
        if dedans(lat, lon, d):
            return True
    if not SEG.get(tuple(deps)):
        SEG[tuple(deps)] = segments(deps)
    return distance_km(lat, lon, SEG[tuple(deps)]) <= 3


faux, n, departs = [], 0, []
for ac in catalog:
    data = json.loads((ROOT/'aide/data'/f"{ac['slug']}.json").read_text())
    for l in data['lieux']:
        n += 1
        if not dans(l['lat'], l['lon'], ac['deps']):
            faux.append((ac['slug'], l['n'], l['cp'], l['lat'], l['lon']))
    ly = json.loads((ROOT/'aide/data/lycees'/f"{ac['slug']}.json").read_text())['lycees']
    for c in data['colleges'] + ly:
        if not dans(c['lat'], c['lon'], ac['deps']):
            departs.append((ac['slug'], c['n'], c['v'], c['lat'], c['lon']))
assert not faux, f'{len(faux)} lieux hors de leur académie : {faux[:5]}'
print(f'{n} lieux : tous dans leur académie')
assert not departs, f'{len(departs)} collèges ou lycées de départ hors de leur académie : {departs[:5]}'
print('Collèges et lycées de départ : tous dans leur académie')
