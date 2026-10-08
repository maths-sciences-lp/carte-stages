# Trouve ton stage : préparation nationale

Les données nationales sont préparées dans le dépôt séparé
`maths-sciences-lp/carte-stages-donnees`. La carte `/` et les liens de classes conservent leur interface francilienne,
mais utilisent les mêmes fichiers nationaux. Les anciens fichiers `data/` sont
conservés ; seul `data/lycees.json` reste utilisé par la carte historique.
L’entrée nationale est `/stage/france/`, puis `/stage/<académie>/`.
Le choix d’académie utilise `commun/academie.js` sans modification.

## Sources et correspondances

- Entreprises : [API Recherche d’entreprises](https://recherche-entreprises.api.gouv.fr/docs/),
  répertoire Sirene. Personnes morales diffusibles, établissements actifs,
  géolocalisés ; mêmes tranches d’effectifs d’entreprise que la méthode historique.
- Lycées : [annuaire de l’Éducation nationale](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/),
  établissements ouverts proposant la voie professionnelle. Les établissements
  sans coordonnées sont recensés dans `bilan.json`, sans position inventée.
- Formations et secteurs : tables de `43a2d51`, après les PR 8 et 9 :
  252 CAP/bacs pro, 122 types d’entreprises, 357 codes NAF. Les familles de
  seconde professionnelle et les BMA sont repris de `aides.py`.
- Indications d’alternance : [API La bonne alternance](https://api.apprentissage.beta.gouv.fr/),
  export national lu en flux, limité aux SIRET déjà présents dans les catalogues.
  Le badge « recruteur potentiel » ne garantit pas l’accueil en stage.

La table associe des diplômes à des types d’activité, pas à des entreprises
individuellement validées. Un code NAF peut couvrir plusieurs métiers. Le repli
sur l’activité de l’unité légale suit la méthode historique. Les cinq fiches
officielles contrôlées et leurs limites sont dans `stage_verifications.json`.
Les entrepreneurs individuels et les informations de contact des personnes
ne sont pas conservés dans les données nationales.

## Collecte reprenable

Travailler dans une copie séparée et vérifier qu’aucun collecteur n’est actif
avant de lancer la commande. Une seule collecte à la fois.

```sh
PYTHONDONTWRITEBYTECODE=1 caffeinate -i python3 -u source/telecharger.py \
  --national \
  --cache "$HOME/.cache/carte-stages-national-naf-962f31271c45" \
  --rate 5 --workers 5
```

Les cinq travailleurs partagent le même plafond global de cinq requêtes par
seconde. Les requêtes en échec sont réessayées avec une attente croissante.
Après huit essais, l’exécution échoue en conservant les fichiers déjà valides.
Le journal de l’exécution d’octobre ne compte pas séparément les erreurs HTTP
intermédiaires récupérées par ces reprises : ne pas les présenter comme nulles.

La collecte parcourt les régions et découpe les requêtes dépassant le plafond
de résultats de l’API. La pagination des établissements d’une même entreprise
est également parcourue. Chaque page est enregistrée après filtrage, puis
chaque département est dédoublonné par SIRET. Relancer la même commande reprend
les pages et départements terminés. Les fichiers `.part` ne sont pas réutilisés.

L’empreinte SHA-256 des codes triés, joints par un saut de ligne sans saut final,
est `962f31271c4579c4ee5dfe8c5a4aaefa7749b981c62e3ca72e86a72a11d8d3c5`.
`configuration-collecte.json` empêche d’utiliser un cache d’une autre liste.
Un cache non vide sans provenance est refusé. Ne jamais réutiliser l’ancien
cache `carte-stages-national`. Pour une nouvelle campagne annuelle, choisir
un dossier neuf : une reprise ne rafraîchit pas les pages déjà téléchargées.

## Génération du dépôt de données

```sh
PYTHONDONTWRITEBYTECODE=1 python3 source/build_domaines.py --national \
  --cache "$HOME/.cache/carte-stages-national-naf-962f31271c45" \
  --sortie "$HOME/Developer/carte-stages-donnees-france" \
  --onisep /cache/605340ddc19a9.csv
```

La génération exige les 101 départements des 30 académies. `--academies` permet
un aperçu local limité, marqué `complet: false`, qui ne doit pas être publié
comme couverture nationale. Le dépôt de sortie doit être une copie Git séparée.
Les fichiers sont découpés en `sirene/<département>/<secteur>.json` et
`lycees/<département>.json`. `catalogue.json` fournit tailles, empreintes,
départements et formations ; `bilan.json` détaille exclusions et volumes.
Le complément Onisep conserve les établissements existants et consigne les cas
incertains dans `rapport-lycees-onisep.json`. Les catalogues légers sont générés
automatiquement ; un aperçu régional incomplet ne produit pas de catalogue IDF.
Les établissements sans nom utilisable sont exclus et comptés, sans nom inventé.

Les pages chargent les secteurs utiles autour du point de départ, y compris
un département voisin d’une autre région. « Toute la région » élargit à la
région de l’académie. La liste conserve tous les résultats ; la carte limite
ses points aux 1 500 premiers, avec une explication visible.

## La bonne alternance et mise à jour mensuelle proposée

```sh
PYTHONDONTWRITEBYTECODE=1 python3 source/lba.py --national \
  --root "$HOME/Developer/carte-stages-donnees-france" --write
```

Sans `--write`, seul un bilan est produit. Le mode national refuse un catalogue
incomplet ou dont les fichiers ne correspondent pas aux empreintes.
Il ne modifie pas `data/lba/` du site. L’option historique `--idf-root` reste
compatible mais n’est plus utilisée par `maj-lba.sh` : les deux cartes lisent
l’export national. La clé reste en mémoire ; ni clé, ni URL signée, ni export
brut ne sont écrits dans les dépôts.

Le script `source/maj-lba.sh` est une **proposition à relire**. Il crée une copie
Git du code et une des données, mais prépare uniquement l’enrichissement LBA
national. Sans argument, il ne pousse rien. Un export incomplet ou invalide
préserve les derniers fichiers servis. Après validation explicite, `--publier`
ne pousse que la copie des données, sans réécriture d’historique. Les bases Git
sont contrôlées avant ce push. La tâche installée n’est pas modifiée ici ; le
lanceur qui récupère le script de main utilisera sa nouvelle version après fusion.

## Contrôles et validation avant fusion

- `python3 -m unittest discover -s source -p test_stage_national.py` : reprise
  du cache, correspondances, exclusions, export LBA incomplet et restauration
  des deux versions sur échec simulé.
- `source/verif_idf.py --donnees-nationales /copie/donnees` : régénérations
  historiques, 175 fichiers conservés et autres pages identiques ; contrat des
  adresses de la carte, 180 clés, 469 UAI, 62 parcours à 320/375 px, frontières,
  clavier et mesures. Voir `verification-idf-national/RAPPORT.md`.
- Lyon, Lille, Aix-Marseille, Rennes, La Réunion : adresse directe, localisation
  simulée, ville saisie, changement d’académie, données réelles et erreurs navigateur.
- Les temps mesurés localement avec un processeur ralenti ne remplacent pas une
  mesure sur téléphone et réseau mobile réels. Les limites figurent dans le rapport.
- Les ressources `commun/accessibilite.css` et `.js`, libellés visibles et lien
  « Accessibilité » sont conservés. La déclaration `/accessibilite/` devra étendre
  son périmètre à ces pages après validation ; les tests automatiques seuls ne
  justifient pas une déclaration de conformité RGAA complète.

Ouvrir deux PR liées, sans fusion ni activation de Pages. L’historique de
`carte-stages` ne doit jamais être réécrit. Toute réduction future de celui du
dépôt de données nécessite une sauvegarde et un accord explicite de Naïm.

## Textes proposés pour une mise à jour après validation

Ces textes sont proposés dans la PR ; la FAQ, le livret, la fiche des sources
et la déclaration d’accessibilité ne sont pas modifiés par cette préparation.

**FAQ — Je cherche un stage ailleurs qu’en Île-de-France.**
Ouvre [Trouve ton stage — France](https://maths-sciences-lp.github.io/carte-stages/stage/france/).
Choisis ton académie avec ta ville, la liste des académies ou le bouton
« Me localiser ». Tu peux refuser la localisation et taper ta ville.
Choisis ensuite ta formation et ton point de départ. Les entreprises proches
s’affichent, y compris dans un département voisin. Pour élargir ta recherche,
choisis « Toute la région ». Les anciens liens de classe gardent leur contenu.

**FAQ — Ces entreprises prennent-elles forcément des stagiaires ?**
Non. Leur type d’activité correspond à des pistes pour ta formation. Appelle
l’entreprise pour savoir si elle peut te recevoir. Vérifie avec ton professeur
que les activités proposées conviennent à ton stage. Le badge « Recruteur
potentiel en alternance » donne une indication supplémentaire ; il ne garantit
pas une place en stage.

**Livret et présentation — couverture nationale.**
Trouve ton stage dispose d’une entrée nationale, par académie, qui permet de
chercher les entreprises autour de son domicile ou de son lycée. Les données
sont chargées par département et par type d’entreprise. Les liens déjà diffusés
en Île-de-France sont conservés. Le nombre d’établissements et la date de collecte
à insérer sont ceux du bilan final joint à la PR, après les exclusions.

**Fiche des sources — préparation des données.**
Sirene via l’API Recherche d’entreprises, annuaire de l’Éducation nationale et
La bonne alternance. Les entreprises sont rapprochées des formations grâce à
la table auditée (fiches Onisep, RNCP/ROME et indices LBA), sans garantie
d’accueil en stage. Les données nationales sont hébergées dans un dépôt séparé,
sur le même domaine GitHub Pages. Les dates, volumes et cas incertains sont
documentés dans le bilan de préparation. Les offres sont masquées à expiration ;
les indications anciennes sont masquées suivant les durées de `lba/meta.json`.

**Déclaration d’accessibilité — périmètre à compléter.**
Ajouter `/stage/france/` et les 30 pages d’académie au périmètre des pages testées,
avec les dates et résultats réellement obtenus dans la PR. Conserver le niveau
de conformité annoncé jusqu’à un audit approprié : les contrôles axe, les tests
de navigation et les ressources issues de la PR 6 ne constituent pas à eux seuls
un audit exhaustif des critères RGAA.
