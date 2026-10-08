"""Page « Mon lycée » : index et fichiers d'académie cohérents ; chaque lien « Après mon diplôme »
mène à un diplôme qu'Après le lycée connaît pour ce lycée ; lycée Hénaff présent."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
catalog = {a['slug'] for a in json.loads((ROOT/'commun/academies.json').read_text())}
index = json.loads((ROOT/'lycee/data/index.json').read_text())
assert len(index) > 3000 and len({r[0] for r in index}) == len(index)
par_ac = {}
for u, n, v, ac in index:
    assert ac in catalog and re.fullmatch(r'\d{7}[A-Z]', u), (u, ac)
    par_ac.setdefault(ac, set()).add(u)
liens = 0
for ac, uais in par_ac.items():
    data = json.loads((ROOT/'lycee/data'/f'{ac}.json').read_text())
    assert set(data) == uais, ac
    dips = json.loads((ROOT/'formation/data'/f'{ac}.json').read_text())['dip']
    for u, ly in data.items():
        assert ly['f'], (ac, u)
        for t, nom, fid, cle, apres in ly['f']:
            assert t in {'2de pro', 'Bac pro', 'CAP', 'CAP agricole', 'BMA'}
            assert not cle or re.fullmatch(r'[a-z0-9-]+', cle)
            if apres:
                assert u in dips[apres]['ly'], (ac, u, apres)
                liens += 1
assert any(r[0] == '0932119Y' for r in index)
print(f'{len(index)} lycées, {len(par_ac)} académies, {liens} liens « Après mon diplôme » vérifiés')
