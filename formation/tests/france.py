"""« Chercher dans toute la France » (data/france/) : chaque lieu d'une page d'académie
se retrouve à l'identique dans le fichier national de sa poursuite, avec le même chiffre
Parcoursup ; pas de courriel ; taille raisonnable.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'formation/data'
fr = {}
for p in sorted((DATA/'france').glob('*.json')):
    if p.name == 'bilan.json':
        continue
    d = json.loads(p.read_text())
    assert p.stem == d['o'].rsplit('.', 1)[-1], p
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', p.read_text()), p
    assert len(p.read_bytes()) < 600_000, p
    assert d['e'] and all(e['af'] == e['o'] for e in d['e']), p
    fr[d['o']] = d
n = 0
for p in sorted(DATA.glob('*.json')):
    if p.name.startswith(('bilan', 'ile-de-france')) or p.name.endswith('-parcoursup.json'):
        continue
    a = json.loads(p.read_text())
    ps = json.loads(p.with_name(p.stem+'-parcoursup.json').read_text())['f']
    for k, f in a['suites'].items():
        nat = fr[f['o']]
        assert {c: nat[c] for c in ('n', 't', 'o')} == {c: f[c] for c in ('n', 't', 'o')}, (p.name, k)
        lieux = {e['o']: e for e in nat['e']}
        for e in f['e']:
            x = lieux[e['o']]
            assert {c: v for c, v in x.items() if c != 'ps'} == e, (p.name, k, e['n'])
            assert x.get('ps') == ps.get(f['o'].rsplit('.', 1)[-1]+'|'+e['o'].rsplit('.', 1)[-1]), (p.name, k, e['n'])
            n += 1
print(f'{len(fr)} poursuites nationales ; {n} lieux d’académie retrouvés à l’identique (Parcoursup compris)')
