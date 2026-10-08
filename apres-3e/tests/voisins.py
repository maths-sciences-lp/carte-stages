"""Lycées des académies voisines (mission 8.6) : chaque lieu ajouté vient tel quel d'une autre
académie (sans les premiers vœux de Créteil), est marqué « x », est bien placé et se trouve à
moins de 30 km de la limite ; aucun lieu de l'académie elle-même.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'source'))
from apres3e_voisins import IDF, RAYON, distance_km, segments  # noqa: E402

catalog = json.loads((ROOT/'commun/academies.json').read_text())
DATA = ROOT/'apres-3e/data'
src = {}
for a in catalog:
    for f in json.loads((DATA/f"{a['slug']}.json").read_text())['formations']:
        for e in f['e']:
            src[(f['n'], e['o'])] = (a['slug'], f, e)
groupes = [(a['slug'], {a['slug']}, a['deps']) for a in catalog]
groupes.append(('ile-de-france', set(IDF), [d for a in catalog if a['slug'] in IDF for d in a['deps']]))
total = 0
for slug, membres, deps in groupes:
    v = json.loads((DATA/f'{slug}-voisins.json').read_text())
    assert v['rayon_km'] == RAYON == 30
    segs = segments(deps)
    for f in v['formations']:
        for e in f['e']:
            origine, fo, eo = src[(f['n'], e['o'])]
            assert origine not in membres, (slug, e['n'])
            attendu = {k: x for k, x in eo.items() if k != 'p'} | {'du': eo.get('du', fo['du']), 'x': 1}
            assert e == attendu, (slug, f['n'], e['n'])
            assert distance_km(e['lat'], e['lon'], segs) <= RAYON + 0.01, (slug, e['n'])
            total += 1
print(f'{len(groupes)} fichiers de voisins ; {total} lieux vérifiés (origine, données, distance ≤ {RAYON} km)')
