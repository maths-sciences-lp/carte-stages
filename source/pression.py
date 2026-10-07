"""Affectation 2025 (Affelnet, académie de Créteil) : capacité et premiers vœux par formation et par lycée.

Source : Draio site Créteil, « Bilans de l'orientation et de l'affectation 2025 », annexe
Taux-de-pression.xlsx (feuille « Tour principal »), https://orientation.ac-creteil.fr/bilans-de-laffectation-de-lorientation/
Document public, réutilisable en citant la source (mentions légales de l'académie de Créteil).
Seules la capacité d'affectation et les premiers vœux (V1) sont gardés, palier 3e, voie professionnelle.

    python3 pression.py Taux-de-pression.xlsx   -> pression_2025.json (à côté de apres3e.py)
Nécessite openpyxl.
"""
import json, re, sys
import openpyxl

wb = openpyxl.load_workbook(sys.argv[1] if len(sys.argv) > 1 else 'Taux-de-pression.xlsx', data_only=True)
rows = list(wb['Tour principal'].iter_rows(values_only=True))
H = rows[0]
out = []
for r in rows[1:]:
    r = dict(zip(H, r))
    if not r['Département'] or r['Palier'] != '3e' or not re.match(r'(2NDPRO|1CAP2|2DPROA|1CAP2A)\b', r['Libellé formation OF'] or ''):
        continue
    if not isinstance(r['V1'], int) or not isinstance(r['Capacité affectation OF'], int):
        continue
    out.append(dict(u=r['Identifiant établissement OF'], l=r['Libellé formation OF'], c=r['Capacité affectation OF'], v=r['V1']))
json.dump(out, open('pression_2025.json', 'w'), ensure_ascii=False, indent=0)
print(len(out), 'lignes')
