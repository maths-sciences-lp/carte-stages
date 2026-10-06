# Fabrication de « Trouve ton stage »

1. `formations.py` puis `formations2.py` : liste des CAP et bacs pro des lycées d'Île-de-France (effectifs du ministère, rentrée 2025, `fr-en-lycee_pro-effectifs-niveau-sexe-mef`) avec les noms Onisep (`Idéo-Formations initiales en France`).
2. `domaines.py` : 19 domaines, 80 secteurs, codes d'activité NAF. `formation_secteurs.json` : secteurs conseillés pour chaque formation (table relue à la main). `aides.py` : sigles tapés par les élèves, images des domaines, familles de métiers de 2nde.
3. `telecharger.py` : établissements actifs d'Île-de-France, sociétés d'au moins un salarié, via l'API Recherche d'entreprises (`limite_matching_etablissements=100`). Reprend là où il s'est arrêté (`idf/fait.txt`).
4. `adresses.py` rend les adresses lisibles (minuscules, abréviations développées, repère à part). `build_domaines.py <dossier>` : écrit `data/` (un fichier par secteur, `index.json`, `lycees.json` depuis l'annuaire de l'éducation). Exclut les entrepreneurs individuels et les données non diffusibles.
5. `public3_template.html` est copié tel quel en `index.html`.
6. `raccourcis.py <dossier>` : liens courts par classe du lycée Eugène Hénaff (`/tne/`, `/tma/`…) et page `/henaff/`. Après une mise à jour des données, changer `const DV` dans `index.html`.
7. `faq/index.html` : questions fréquentes (élèves, enseignants, entreprises), page statique écrite à la main ; liens depuis le pied de la carte et la page `/henaff/`.
