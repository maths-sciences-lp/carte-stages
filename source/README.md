# Fabrication de « Trouve ton stage »

1. `formations.py` puis `formations2.py` : liste des CAP et bacs pro des lycées d'Île-de-France (effectifs du ministère, rentrée 2025, `fr-en-lycee_pro-effectifs-niveau-sexe-mef`) avec les noms Onisep (`Idéo-Formations initiales en France`).
2. `domaines.py` : 19 domaines, 80 secteurs, codes d'activité NAF. `formation_secteurs.json` : secteurs conseillés pour chaque formation (table relue à la main). `aides.py` : sigles tapés par les élèves, images des domaines, familles de métiers de 2nde.
3. `telecharger.py` : établissements actifs d'Île-de-France, sociétés d'au moins un salarié, via l'API Recherche d'entreprises (`limite_matching_etablissements=100`). Reprend là où il s'est arrêté (`idf/fait.txt`).
4. `adresses.py` rend les adresses lisibles (minuscules, abréviations développées, repère à part). `build_domaines.py <dossier>` : écrit `data/` (un fichier par secteur, `index.json`, `lycees.json` depuis l'annuaire de l'éducation). Exclut les entrepreneurs individuels et les données non diffusibles.
5. `public3_template.html` est copié tel quel en `index.html`.
6. `raccourcis.py <dossier>` : liens courts par classe du lycée Eugène Hénaff (`/tne/`, `/tma/`…) et page `/henaff/`. Après une mise à jour des données, changer `const DV` dans `index.html`.
7. `faq/index.html` : questions fréquentes (élèves, enseignants, entreprises), page statique écrite à la main ; liens depuis le pied de la carte et la page `/henaff/`.
8. `formation/` : « Après le lycée » (slogan « Trouve ta formation »), pour tous les lycées de l’académie de Créteil. `formations.json` fabriqué par `source/apres_lycee.py` (à lancer dans le dossier des fichiers Onisep) : diplômes de départ = CAP, CAP agricole, bac pro et BMA préparés en lycée dans l’académie (Idéo-Actions de formation initiale, univers lycée) ; poursuites = rubrique « Exemple(s) de formation(s) » des fiches diplômes Onisep (une page par diplôme, téléchargée lentement dans `fiches/`), lieux en Île-de-France (univers lycée + enseignement supérieur). Les 11 classes du lycée Eugène Hénaff gardent leurs listes relues à la main (`source/suites.py`) et leurs boutons en haut de la page ; les anciens liens `formation/#<classe>` marchent toujours, les autres s’écrivent `formation/#d=<n° Onisep>&ly=<UAI>`. (`formations_apres.py` = ancienne version, lycée Hénaff seul.)
9. `apres-3e/` : « Après le collège » (slogan « Trouve ta formation », académie de Créteil). `apres3e.json` fabriqué par `source/apres3e.py` (données Onisep voie scolaire : 2de pro, CAP, bac pro ; collèges de l’annuaire de l’Éducation nationale) ; domaines parlants dans `source/domaines_apres3e.py`, corrections manuelles relues dans `source/corrections_apres3e.py`.
10. `accueil/` : page commune (Trouve ton stage, Après le collège, Après le lycée ; les adresses ne changent jamais, des liens ont été envoyés), cible de maths-sciences-pro.fr/stages/. Chiffres InserJeunes (sortants 2023-2024, data.education.gouv.fr, Licence Ouverte) reliés par `source/inserjeunes.py` (même UAI, même diplôme, même option).

## Enrichissement La Bonne Alternance

`lba.py` utilise l'export national officiel (`GET /api/job/v1/export`), puis
rapproche ses opportunités des seuls SIRET déjà présents dans les fichiers
sectoriels de la carte. Il ne modifie pas les données Sirene et n'ajoute aucune
entreprise : les exclusions existantes restent applicables. L'export est lu en
flux, sans enregistrer le fichier national ni son URL signée.

La clé reste hors du dépôt, dans
`~/Library/Application Support/carte-stages/lba-api-key` (permissions `600`),
ou dans la variable d'environnement `LBA_API_KEY`. Ne jamais mettre la clé dans
le HTML, un argument de commande ou un fichier publié.

```sh
python3 source/lba.py          # dry-run : bilan seulement
python3 source/lba.py --write  # écrit seulement data/lba-index.json
```

Le fichier public contient les liens des recruteurs potentiels et au plus trois
offres par entreprise, actives et non expirées, de niveau CAP ou bac (ou de niveau
non précisé). Les offres déléguées à un CFA sont exclues, car leur SIRET peut être
celui du CFA. Aucun téléphone, email, CV ou description intégrale n'est publié.
Les offres peuvent concerner un autre métier que celui choisi par l'élève : leur
intitulé est affiché et l'élève est invité à vérifier métier et diplôme.

Les badges sont des pistes d'alternance, pas une garantie de stage en PFMP. Leur
affichage ne change ni l'ordre par distance ni les entreprises disponibles.
L'enrichissement est facultatif : si le fichier manque ou échoue au chargement,
la carte Sirene reste utilisable. Les liens d'offres expirées sont masqués ; tout
l'enrichissement est masqué après sept jours depuis la date de l'export. Les
données LBA sont renouvelées quotidiennement par leur service : relancer le
script avant une diffusion, changer `DV` dans `index.html` et recopier la page
dans `source/public3_template.html`. Sans mise à jour et publication régulières,
les indications disparaîtront au bout de sept jours.

Documentation officielle :
https://api.apprentissage.beta.gouv.fr/fr/explorer/recherche-offre
et https://api.apprentissage.beta.gouv.fr/fr/documentation-technique.
