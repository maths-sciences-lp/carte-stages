"""Départ « Mon lycée » : un fichier par académie, lycées triés, coordonnées valides, sans courriel."""
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
catalog = json.loads((ROOT/'commun/academies.json').read_text())
total = 0
for ac in catalog:
    p = ROOT/'aide/data/lycees'/f"{ac['slug']}.json"
    texte = p.read_text()
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', texte), p
    ly = json.loads(texte)['lycees']
    assert ly and len(p.read_bytes()) < 200_000, p
    assert ly == sorted(ly, key=lambda x: (x['n'], x['v'])), p
    for x in ly:
        assert set(x) == {'n', 'v', 'u', 'lat', 'lon'} and re.fullmatch(r'\d{7}[A-Z]', x['u']), (p.name, x)
        assert math.isfinite(x['lat']) and math.isfinite(x['lon']), (p.name, x)
    total += len(ly)
assert any(x['u'] == '0932119Y' for x in json.loads((ROOT/'aide/data/lycees/creteil.json').read_text())['lycees'])
print(f'{len(catalog)} académies, {total} lycées : fichiers, tri, coordonnées et lycée Hénaff OK')
