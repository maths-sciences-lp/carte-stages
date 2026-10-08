# Collecte Sirene : contrôle des établissements par le stock officiel

La recherche d'entreprises ne constitue pas une liste exhaustive de leurs
établissements. `matching_etablissements` est limité à 100 ; la tentative
`page_etablissements` ne permet pas de parcourir les sites dans l'API publique.
Le collecteur ne l'utilise plus. `total_results` est un compte approximatif
(agrégation de cardinalité), pas une preuve de complétude. Les doublons entre
pages, les limites de recherche et les listes saturées restent signalés.

## Raccordement à la collecte annuelle

La phase API de `telecharger.py --national` conserve son cache et son format,
mais son bilan indique désormais `non_certifiee_sans_comparaison_stock`.
Avant de proposer les données annuelles à la relecture, effectuer la phase
stock ci-dessous sur chaque groupe de départements autorisé. Elle compare les
SIRET, revérifie les absents individuellement et produit des ajouts uniquement.
La mise à jour mensuelle LBA et sa tâche installée ne changent pas.

Le stock officiel est publié sur
[la fiche Sirene Insee](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret).
Choisir les URL et la date du même millésime `StockEtablissement` et
`StockUniteLegale`, explicitement : ne pas réutiliser le millésime d'octobre 2026
pour une prochaine collecte. Les paramètres de cache sont immuables. Un nouveau
millésime, une autre liste NAF ou un autre périmètre demandent un nouveau cache.
La nomenclature doit être `NAFRev2` ; le passage à NAF 2025 nécessite une mission
séparée, pas une conversion implicite.

Les outils utilisent Python 3, DuckDB et pyproj dans un environnement isolé.
Aucune dépendance n'est ajoutée au navigateur. Les commandes suivantes sont un
gabarit, à renseigner avec des chemins de **copies de travail séparées** et le
périmètre approuvé. Elles ne publient rien.

```sh
# Variables de travail à renseigner ; ne jamais mettre de clé LBA ici.
# PY : Python de l'environnement isolé
# CACHE : nouveau cache du groupe ; DONNEES : worktree carte-stages-donnees
# CACHE_API : cache de la collecte annuelle ; COMMUNES : référentiel de communes
# STOCK_DATE, STOCK_ETAB, STOCK_UL : date et URL officielles vérifiées

# Exemple d'un groupe explicitement autorisé ; choisir des groupes modestes.
"$PY" source/stage_stock_temoin.py --cache "$CACHE" --phase etablissements \
  --departements 75 78 91 92 95 --date-stock "$STOCK_DATE" \
  --url-etablissements "$STOCK_ETAB" --url-unites "$STOCK_UL"
"$PY" source/stage_stock_temoin.py --cache "$CACHE" --phase unites
"$PY" source/verif_stage_rattrapage.py --root "$DONNEES" --cache "$CACHE" --avant
"$PY" source/stage_stock_preparer.py --cache "$CACHE" \
  --cache-national "$CACHE_API" --donnees "$DONNEES" \
  --communes "$COMMUNES" --graine 20261009
"$PY" source/stage_stock_comparer.py --cache "$CACHE" --donnees "$DONNEES"
"$PY" source/stage_stock_verifier.py --cache "$CACHE" --cache-national "$CACHE_API"
"$PY" source/stage_sondage.py --cache "$CACHE" --donnees "$DONNEES"
"$PY" source/stage_bilan_stock.py --cache "$CACHE"
"$PY" source/stage_ajouts.py --root "$DONNEES" --cache "$CACHE" --deps 75 78 91 92 95
# Examiner ce bilan avant l'écriture locale ; worktree de données propre requis.
"$PY" source/stage_ajouts.py --root "$DONNEES" --cache "$CACHE" --deps 75 78 91 92 95 --write
"$PY" source/verif_stage_rattrapage.py --root "$DONNEES" --cache "$CACHE"
```

La vérification finale des liens attend `liens-avant.json`, relevé des 15 liens
Hénaff et de `/henaff/` avant écriture. Le rapport de mission conserve ce relevé
et ses compteurs ; la page, la formation et le lycée doivent rester identiques.
Effectuer aussi les tests navigateur, `verif_idf.py` et `surveillance.py` avant PR.
Ne pas prendre une comparaison au stock pour une certification de l'API en temps réel.

## Filtres et contrôles

- Le stock filtre **l'activité et la tranche d'effectif de l'unité légale**, comme
  les paramètres de recherche de l'API. Unité active, nature juridique autre que
  1000, diffusion ouverte pour l'unité et le site, établissement actif et dans le
  bon département. Les sites sans coordonnées dans le stock restent candidats :
  l'API peut disposer d'une position valide.
- Chaque SIRET absent est revérifié directement, avec les mêmes filtres et le
  même classement par type (`stage_donnees.preparer`). Seules les coordonnées API
  valides sont ajoutées. Les coordonnées Lambert du stock servent au contrôle
  comparatif, sans remplacer automatiquement une position. La comparaison
  Lambert 93 est adaptée à la métropole ; l'outre-mer demande un contrôle de CRS
  spécifique avant utilisation de ce diagnostic de distance.
- Une entreprise n'est exclue du rattrapage que si chaque SIRET candidat du stock
  est déjà présent **dans le même département**. Aucun total national ne peut
  compenser un site absent localement.
- Tirer 100 couples entreprise/département exclus parmi les entreprises multisites
  observées dans le stock local ou le cache national. La graine, la population et
  la liste exacte sont conservées. Revérifier tous leurs SIRET du stock et ceux du
  cache qui servent d'explication, puis chercher par nom et communes avec contrôle
  exact du SIREN. Paris utilise ses arrondissements. Si une omission admissible est
  trouvée : ne pas appliquer les ajouts, élargir la sélection et refaire un sondage
  enregistré distinctement. Les listes saturées et recherches non résolues restent
  des limites explicites ; elles ne deviennent jamais une preuve de complétude.
- Le témoin historique `data/` est contrôlé SIRET par SIRET. Les écarts entre la
  date du stock et celle de l'API sont consignés sans inventer une date de fermeture.
- Les ajouts passent l'export LBA en vigueur. L'export complet et la clé ne sont
  jamais enregistrés dans les preuves. Les lignes déjà publiées, Sirene et LBA,
  restent inchangées. Les catalogues, empreintes et tailles sont recalculés.

## Disque, reprise et preuves

Vérifier `df` avant chaque phase. Les appels réseau s'arrêtent sous 2 Go libres.
Le relais Parquet n'accepte que des lectures HTTP partielles bornées et des
réponses 206 ; il applique un budget de transfert. Le stock national complet
n'est jamais écrit sur le Mac. La consommation réseau dépasse la taille de
l'extrait local car les groupes Parquet ne sont pas triés par département.
DuckDB est limité à 384 Mo de mémoire et 256 Mo de fichiers temporaires lors de
l'extraction. Les deux extraits IDF d'octobre 2026 représentent environ 194 Mo.

Les contrôles API sont limités à 5 requêtes/s au total, 5 travailleurs ; les 429
respectent `Retry-After` et ralentissent tous les travailleurs. Un verrou empêche
deux vérifications dans le même cache. Ne pas lancer deux caches en parallèle.
Les réponses sont minimisées : aucun dirigeant, contact ou entrepreneur individuel
n'est archivé comme entreprise admissible. Les contrôles terminés sont repris
sans requête supplémentaire. Un ajout déjà appliqué n'est pas répété.

Conserver : configurations, URL/date/SHA-256 des extraits, bilans, listes SIRET,
statuts et motifs, sondages, journaux de requêtes, contrôles des liens, manifeste
avant/après et compte rendu des vérifications dans l'Annuaire des entreprises.
Après les contrôles réussis, les extraits Parquet peuvent être supprimés en
consignant leur SHA-256 et leur taille ; les preuves JSON/CSV restent conservées.
Le cache ne doit pas être copié intégralement dans Git. Les PR contiennent les
rapports utiles à la relecture, pas les millions de lignes du stock.

## Limite de classement conservée

La recherche sélectionne les entreprises par le NAF de leur unité légale. Le
classement utilise l'activité du site si l'API la fournit, sinon le NAF de l'unité
légale comme repli. Un site d'une autre activité peut ainsi suivre le classement
de l'entreprise : cas signalé AKENA, SIRET `42040340401427`, entrepôt `52.10B`
classé `43.32B`. Ce comportement historique n'est pas modifié dans la mission 8.8.
