# Fabrication de « Trouve ton stage »

1. `formations.py` puis `formations2.py` : liste des CAP et bacs pro des lycées d'Île-de-France (effectifs du ministère, rentrée 2025, `fr-en-lycee_pro-effectifs-niveau-sexe-mef`) avec les noms Onisep (`Idéo-Formations initiales en France`).
2. `domaines.py` : 19 domaines, 86 secteurs, codes d'activité NAF. `formation_secteurs.json` : secteurs conseillés pour chaque formation (chaque lien vérifié avec la fiche Onisep du diplôme, octobre 2026). `aides.py` : sigles tapés par les élèves, images des domaines, familles de métiers de 2nde.
3. `telecharger.py` : établissements actifs d'Île-de-France, sociétés d'au moins un salarié, via l'API Recherche d'entreprises (`limite_matching_etablissements=100`). Reprend là où il s'est arrêté (`idf/fait.txt`).
4. `adresses.py` rend les adresses lisibles (minuscules, abréviations développées, repère à part). `build_domaines.py <dossier>` : écrit `data/` (un fichier par secteur, `index.json`, `lycees.json` depuis l'annuaire de l'éducation). Exclut les entrepreneurs individuels et les données non diffusibles.
5. `public3_template.html` est copié tel quel en `index.html`.
6. `raccourcis.py <dossier>` : liens courts par classe du lycée Eugène Hénaff (`/tne/`, `/tma/`…) et page `/henaff/`. Après une mise à jour des données, changer `const DV` dans `index.html`.
7. `faq/index.html` : questions fréquentes (élèves, enseignants, entreprises), page statique écrite à la main ; liens depuis le pied de la carte et la page `/henaff/`.
8. `formation/` : « Après le lycée » (slogan « Trouve ta formation »), pour tous les lycées de l’académie de Créteil. `formations.json` fabriqué par `source/apres_lycee.py` (à lancer dans le dossier des fichiers Onisep) : diplômes de départ = CAP, CAP agricole, bac pro et BMA préparés en lycée dans l’académie (Idéo-Actions de formation initiale, univers lycée) ; poursuites = rubrique « Exemple(s) de formation(s) » des fiches diplômes Onisep (une page par diplôme, téléchargée lentement dans `fiches/`), lieux en Île-de-France (univers lycée + enseignement supérieur). Les 11 classes du lycée Eugène Hénaff gardent leurs listes relues à la main (`source/suites.py`) et leurs boutons en haut de la page ; les anciens liens `formation/#<classe>` marchent toujours, les autres s’écrivent `formation/#d=<n° Onisep>&ly=<UAI>`. (`formations_apres.py` = ancienne version, lycée Hénaff seul.)
   Chiffres Parcoursup des BTS et BTSA (session 2025, `fr-esr-parcoursup`, data.enseignementsup-recherche.gouv.fr, Licence Ouverte) : `source/parcoursup.py` écrit `formation/parcoursup.json` (places, candidats, admis, admis venant d’un bac pro). Les lieux Onisep n’ont pas d’UAI : rapprochement par spécialité et option, puis même site (moins de 100 m) ou nom d’établissement proche à moins de 2 km. 672 lieux de BTS sur 885 reliés ; les autres sont surtout des écoles privées absentes de Parcoursup. Relancer chaque année quand la nouvelle session est publiée, puis changer `?v=` du `fetch('parcoursup.json…')` dans `formation/index.html`.
9. `apres-3e/` : « Après le collège » (slogan « Trouve ta formation », académies de Créteil, Paris et Versailles). `apres3e.json` fabriqué par `source/apres3e.py` (données Onisep voie scolaire : 2de pro, CAP, bac pro ; collèges de l’annuaire de l’Éducation nationale) ; domaines parlants dans `source/domaines_apres3e.py`, corrections manuelles relues dans `source/corrections_apres3e.py`. Premiers vœux et places 2025 : `pression.py` (annexe Taux-de-pression.xlsx du bilan de l’affectation, Draio Créteil) puis `pression_correspondance.json` (94 intitulés Affelnet → intitulés Onisep).
10. `accueil/` : page commune (Trouve ton stage, Après le collège, Après le lycée, Qui peut m’aider ? ; les adresses ne changent jamais, des liens ont été envoyés), cible de maths-sciences-pro.fr/stages/. Chiffres InserJeunes (sortants 2023-2024, data.education.gouv.fr, Licence Ouverte) reliés par `source/inserjeunes.py` (même UAI, même diplôme, même option).
11. `aide/` : « Qui peut m’aider ? » (Île-de-France ; maisons des adolescents de Paris et Versailles dans `mda_idf.json`). `aide.json` fabriqué par `source/aide.py` : CIO, missions locales et Info Jeunes de l’annuaire Service-public.fr (API api-lannuaire, sans les noms des agents) ; maisons des adolescents saisies d’après l’ARS Île-de-France et anmda.fr (le type « mda » de l’annuaire désigne les maisons de l’autonomie) ; bibliothèques municipales et intercommunales du ministère de la Culture (enquête 2023, data.gouv.fr ; associatives et points ouverts moins de 4 h par semaine écartés).

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
python3 source/lba.py --write  # écrit seulement data/lba/ (un fichier par secteur + meta.json)
```

Le fichier public contient les liens des recruteurs potentiels et au plus trois
offres par entreprise, actives et non expirées, de niveau CAP ou bac (ou de niveau
non précisé). Les offres déléguées à un CFA sont exclues, car leur SIRET peut être
celui du CFA. Aucun téléphone, email, CV ou description intégrale n'est publié.
Les offres peuvent concerner un autre métier que celui choisi par l'élève : leur
intitulé est affiché et l'élève est invité à vérifier métier et diplôme.

Les badges sont des pistes d'alternance, pas une garantie de stage en PFMP. Leur
affichage ne change ni l'ordre par distance ni les entreprises disponibles.
L'enrichissement est facultatif : si les fichiers manquent ou échouent au chargement,
la carte Sirene reste utilisable. Chaque secteur a son petit fichier
`data/lba/<secteur>.json`, chargé seulement quand l'élève choisit ce secteur ;
`data/lba/meta.json` donne la date de l'export. Le badge « recruteur potentiel »
est masqué 31 jours après cette date ; chaque offre est masquée à sa date
d'expiration (ou 7 jours après l'export si elle n'en a pas).

Les données LBA sont renouvelées quotidiennement par leur service : relancer le
script avant une diffusion (au moins une fois par mois), changer `DV` dans
`index.html` et recopier la page dans `source/public3_template.html`.

Documentation officielle :
https://api.apprentissage.beta.gouv.fr/fr/explorer/recherche-offre
et https://api.apprentissage.beta.gouv.fr/fr/documentation-technique.


## « Qui peut m’aider ? » — 30 académies

Python 3 et `curl` ; `beautifulsoup4` uniquement pour collecter les fiches ANMDA.
Depuis la racine :

```sh
python3 source/aide.py --academies toutes
python3 source/aide.py --academies lyon lille aix-marseille rennes la-reunion
```

Sorties : `aide/data/<slug>.json` et `aide/<slug>/index.html`. Les petites pages
chargent l’unique application `aide/index.html`, puis `aide/national.js`.
`/aide/france/` ouvre le choix ou l’académie retenue ; `/aide/` reste l’Île-de-France.
Sans paramètre, `aide.py` garde son mode historique : le lancer depuis le dossier
contenant `annuaire-sp.json`, `bibliotheques.json`, `colleges_idf.json` (ou `colleges.json`) ;
il y régénère `aide.json`. Le mode national n’écrit jamais `aide/aide.json`.

Cache reprenable : `~/.cache/carte-stages-aide/` (`--cache`). Pour actualiser, choisir
un cache vide et ajouter `--refresh-mda` ; sinon le relevé `aide/data/mda-france.json`
est réutilisé. `--mda-only` collecte ANMDA avec 2,5 s entre téléchargements et un
User-Agent navigateur. Examiner `mda-review.json` dans le cache pour les ateliers ;
les exclusions motivées vont dans `aide/data/mda-exclusions.json`. `bilan.json`
donne les effectifs, tailles, exclusions et requêtes sources exactes.

### Sélecteur réutilisable

`commun/academies.json` est la référence unique : `slug` stable, `nom`, `deps`, `region`.
Elle suit les [30 académies du ministère](https://www.education.gouv.fr/les-regions-academiques-academies-et-services-departementaux-de-l-education-nationale-6557)
et l’[article R222-2](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006071191/LEGISCTA000006151410/),
consultés le 7 octobre 2026. Aucun des 101 départements n’est partagé. Les territoires
non résolus restent signalés dans le [rapport](../aide/verification/rapport.md).

```js
import {initAcademie} from '../commun/academie.js';
await initAcademie({mount, contenu, baseOutil: new URL('./', document.baseURI),
  onSelect: async (academie, {signal}) => { /* charger academie.slug avec signal */ }
});
```

Après `await chargerAcademies()`, `academieDepuisDepartement(code)` et
`academieDepuisAdresse(featureBAN)` renvoient une entrée ou `null` si inconnue/ambiguë.
Le module gère l’URL directe prioritaire, `stages.academie` avec try/catch, la question
et « changer ». Les pages historiques ne le chargent pas. Les contours locaux
`commun/contours/<dep>.json` (index `departements.json`) ne sont chargés qu’au clic GPS,
pour les emprises concernées ; la position reste dans le téléphone. BAN n’est appelé
que pendant la saisie. Les frontières simplifiées peuvent nécessiter le choix par ville.

Sources : [Service-public.fr](https://api-lannuaire.service-public.fr/explore/dataset/api-lannuaire-administration/)
(sans agents ni courriels), [Culture](https://www.data.gouv.fr/datasets/adresses-des-bibliotheques-publiques-2)
(enquête 2023, export 27 août 2025, filtres historiques), [ANMDA](https://anmda.fr/fr/annuaire-mda),
[collèges ouverts](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/) (UAI dédoublonnés),
[contours Etalab/IGN 2025 à 100 m](https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-100m.geojson)
(Licence Ouverte) et [communes](https://geo.api.gouv.fr/decoupage-administratif/communes)
(pour vérifier les codes postaux corses à la génération). Collecte du 7 octobre 2026.

### Vérifications avant PR

```sh
python3 source/verif_idf.py --sources-idf /chemin/du/cache-historique
python3 aide/tests/donnees.py
# Serveur local actif (python3 -m http.server 8765) :
BASE_URL=http://127.0.0.1:8765 node aide/tests/national.cjs
```

Node/Playwright nécessaires (`PLAYWRIGHT_MODULE` si installé hors dépôt).
`verif_idf.py` ne modifie pas le dépôt : il régénère dans un dossier temporaire,
compare les trois JSON à `origin/main` et les dix pages à GitHub Pages à 375 px.
Sources absentes : résultat incomplet (code 2), jamais « oui » par défaut ; différence :
code 1. Rapports et captures : `/tmp/verif-idf/` (`--rapport`) et `/tmp/aide-national/`
(`TEST_OUTPUT`). Le déploiement canonique est utilisé car le domaine `/stages/`
sert `accueil/`, pas la carte racine. La régénération des deux outils de formation
sera ajoutée lors de leurs missions ; leurs fichiers et pages sont déjà comparés.
