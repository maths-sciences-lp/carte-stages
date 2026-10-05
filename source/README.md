# Fabrication

Depuis ce dossier :

1. `python3 prospect.py` puis `python3 prospect2.py` : interroge l'API Recherche d'entreprises (base Sirene) et écrit `prospects.json`.
2. `python3 build_public.py` : écrit `../index.html` à partir de `public_template.html`.

Filtres : établissements actifs de Paris (75) et de Seine-Saint-Denis (93), sociétés d'au moins un salarié, données diffusibles, entrepreneurs individuels exclus.
