# Mission 8.8 — rattrapage Île-de-France, 8 octobre 2026

## Résultat et périmètre

**23 004 établissements uniques ajoutés, 0 retrait et 0 modification des lignes existantes.**
325 236 → 348 240 établissements en Île-de-France (+7,07 %). National :
1 657 440 → 1 680 444, uniquement par les ajouts franciliens. **964/964** témoins
historiques actifs retrouvés. 23 009 lignes de secteurs (5 inscriptions supplémentaires
intersecteurs), 3 260 nouveaux SIRET enrichis par LBA. 546 entreprises/organismes distincts.
Les autres départements ne sont ni collectés ni modifiés. Aucune publication ni fusion.

Les filtres et la table de classement n'ont pas changé (252 formations, 357 NAF ;
SHA-256 des codes triés : `962f31271c4579c4ee5dfe8c5a4aaefa7749b981c62e3ca72e86a72a11d8d3c5`).
Le collecteur garde les lignes Sirene et LBA déjà publiées, même lorsqu'un contrôle actuel
les juge non admissibles ; cette mission ajoute seulement.

| Département | Déjà publiés | Ajoutés | Après | Parmi les 964 | Rejet API | Rejet classement |
|---|---:|---:|---:|---:|---:|---:|
| 75 | 114002 | 7896 | 121898 | 303 | 233 | 221 |
| 77 | 29711 | 2006 | 31717 | 44 | 689 | 115 |
| 78 | 29348 | 2340 | 31688 | 85 | 403 | 101 |
| 91 | 25549 | 1823 | 27372 | 113 | 246 | 125 |
| 92 | 38738 | 3434 | 42172 | 137 | 99 | 132 |
| 93 | 34586 | 2033 | 36619 | 92 | 116 | 85 |
| 94 | 27664 | 1969 | 29633 | 121 | 175 | 92 |
| 95 | 25638 | 1503 | 27141 | 69 | 264 | 93 |

`departements.csv` compte tous les SIRET publiés avant le rattrapage. Le champ historique
`deja_presents` des bilans d'exécution compte seulement les candidats déjà présents et
n'est pas ce total. Les 26 193 absents du témoin stock ont tous un statut : 23 004 ajoutés,
3 189 rejetés. Motifs par département : `rejets-par-departement.json` et les deux listes
`stock-ecarts-expliques.csv`. Aucune absence admissible et classable du témoin ne reste
inexpliquée. Les 2 649 témoins historiques plus larges ont également chacun un statut
(`temoins-historiques.csv`) : 2 436 ajoutés, 213 non ajoutés.

## Sources et dates

- [Stock officiel Sirene Insee](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret), millésime **1er octobre 2026**, établissements et unités légales Parquet. Lecture distante partielle, jamais de stock national écrit sur le Mac. URL exactes, date, taille et SHA-256 des quatre extraits dans les fichiers `stock-*-provenance.json`.
- [API Recherche d'entreprises](https://recherche-entreprises.api.gouv.fr/docs/), vérifications SIRET individuelles le **8 octobre 2026**, 5 requêtes/s, reprise après 429. Actif, diffusible, unité hors nature juridique 1000, NAF et tranche d'effectif de l'unité légale admissibles, département et coordonnées valides.
- Export La bonne alternance du **8 octobre 2026 à 01:01:04 UTC**, réappliqué aux nouveaux SIRET. Ni export intégral ni clé dans Git ; tâche mensuelle installée inchangée.
- Référence données : `5bc8cacd4318787156719480bb86ca435fbb0b99`. Code intégré par merge, sans réécriture : `origin/main` **fc81722f0f2fd085b2120b8cedfc2579eaac5d08**, incluant PR 21 à 29.

## Cause, correctif et collecte annuelle

L'API recherche des entreprises ; sa liste `matching_etablissements` est limitée à 100.
`page_etablissements` ne permet pas d'obtenir les suivants publiquement. Cette tentative
inopérante est retirée. `total_results` est approximatif et ne certifie pas un nombre de
SIRET ; les anomalies de pagination, saturations et doublons restent consignés.
Le stock fournit le témoin SIRET par département, puis chaque absent est contrôlé dans
l'API actuelle avec les filtres d'origine. Voir [le mode opératoire annuel](../STOCK-SIRENE.md).
Le bilan API seul est explicitement `non_certifiee_sans_comparaison_stock` ; la phase stock
est obligatoire avant validation de la prochaine collecte annuelle. Les outils acceptent
un périmètre explicite et un nouveau millésime dans un nouveau cache.

## Sondages et limites

- Créteil : 100 couples entreprise/département sur 33 113 alertes écartées, graine **20261008**, 0 omission et 0 couple non résolu.
- Complément IDF : 100 sur 45 173, graine **20261009**, **0 omission/100**, 0 non résolu. Comparaison au niveau des SIRET du même département, avec recontrôle des sites du cache explicatif et des sites du stock. Référence publiée figée avant ajout, jamais reconstruite sur les données enrichies.
- Trois recherches avec les anciens noms ne trouvaient rien ; elles ont été refaites avec le nom légal actuel obtenu par contrôle direct (BARKENE SURETE, TEAM TOY LILLE, PIMENT INTERIM). Même échantillon et graine. Diagnostic initial conservé, aucune omission masquée.
- Créteil : quatre listes API initiales saturées (SIREN 130012834 en 77 ; 219300050, 130020654, 179304316 en 93). L'ancienne voie géographique avait encore 2 709 couples non parcourus ; la comparaison au stock la remplace, sans prétendre l'avoir terminée.
- Complément IDF : pas de nouvel inventaire exhaustif des listes initiales de l'API (compteur `null`, pas zéro). Les recherches du sondage ont zéro liste saturée/non résolue. Détails `listes-saturees-et-limites.json`.
- Le stock date du 1/10, les contrôles du 8/10. Un changement de statut entre ces dates ne prouve pas une perte de collecte ; aucune date de fermeture n'est inventée. Ce résultat ne certifie pas tous les établissements ouverts après le 1/10 ni le reste de la France.
- Écarts de coordonnées Lambert/API : 9/30 contrôles du pilote et 17/50 du complément atteignent 50 m. Les coordonnées API restent utilisées ; aucun remplacement automatique par le stock.

## Pertinence métier : limite signalée à Naïm

Les établissements ajoutés sont des pistes administrativement admissibles, **pas des offres
de stage ni une garantie d'accueil**. Les 2 766 SIRET « Ville de Paris » correspondent à
2 337 adresses distinctes : services administratifs, crèches, équipements sportifs,
ateliers, etc. Le classement historique peut produire des rapprochements peu pertinents,
notamment les bains-douches dans « esthétique et soins de beauté ».
La sélection emploie le NAF de l'unité légale ; le classement emploie celui du site quand
l'API le fournit, sinon celui de l'unité légale. Cas déjà signalé : AKENA
`42040340401427`, entrepôt 52.10B classé 43.32B. Aucun changement de classement dans cette PR.
Un contrôle métier séparé est proposé, en priorité pour les organismes multisites.

## Contrôles Annuaire

Cinq ajouts du pilote et cinq du complément ont été lus sur les fiches publiques de
l'Annuaire ; noms, adresses, activité/état et nature juridique dans
`*/verification-annuaire-resultats.json`. Complément : Lagardère Paris
`54209533605566`, Engie Versailles `55204695507972`, Caisse d'Épargne Vigneux
`38290094200378`, APF Bagneux `77568873206803`, ME Group Saint-Brice `59203393008065`.
Tirage du complément : graine **20261010**. Un premier candidat du 95, Maisons Pierre,
actif dans l'Annuaire, a été rejeté pour absence de position API ; le candidat suivant du
tirage a été contrôlé. Ce rejet est conservé dans le rapport.

## Liens Hénaff et navigateur

Les 15 formations et leur lycée `0932119Y` sont inchangés, ainsi que les octets des
redirections et de `/henaff/`. Comparaison **collecte nationale du 8/10 avant rattrapage →
après rattrapage**, pas l'ancien jeu du 5/10 :

| Lien | À 5 km d'Hénaff | Toute l'Île-de-France |
|---|---:|---:|
| /tne | 1468 → 1576 | 16727 → 18154 |
| /mnb | 3773 → 4335 | 36185 → 38489 |
| /mama | 628 → 631 | 5554 → 5573 |
| /iccer | 777 → 838 | 8574 → 9544 |
| /mee | 777 → 838 | 8574 → 9544 |
| /tma | 601 → 601 | 5297 → 5299 |
| /era | 601 → 601 | 5297 → 5299 |
| /eeb | 3683 → 4242 | 34368 → 36621 |
| /geometre | 1394 → 1955 | 19326 → 21621 |
| /mit | 758 → 777 | 8223 → 8429 |
| /sdg | 786 → 786 | 5627 → 5654 |
| /ebeniste | 601 → 601 | 5297 → 5299 |
| /bma-ebeniste | 628 → 631 | 5554 → 5573 |
| /bma-signaletique | 786 → 786 | 5627 → 5654 |
| /ma | 601 → 601 | 5297 → 5299 |

62 parcours navigateur à 320/375 px ; 180 clés historiques, 469 UAI, clavier,
Maison persistante, stockage refusé, LBA, reprise HTTP 503, frontières et page Hénaff
vérifiés sans erreur (`carte-contrat.json`). Le rapport `verif-idf.txt` utilise aussi son
ancien témoin du 5/10 : les retraits qu'il y mentionne appartiennent à la migration
antérieure, **pas au rattrapage présent**, qui vérifie indépendamment zéro retrait.

## Non-régression et écart hors périmètre

32 tests unitaires avec DuckDB : OK. Tests des données des trois outils et des voisins,
et 5 566 lycées d'aide : OK. `surveillance.py` :
`Tout répond : pages, données et mises à jour La bonne alternance.` (site public actuel,
complété par les contrôles locaux des données proposées).
Idempotence : **21 601 fichiers aux empreintes inchangées** après seconde application ;
recalcul indépendant des deux caches : zéro nouvel ajout (`idempotence.json`).
Contrôle indépendant : **12 322 empreintes**, 266 648 anciennes lignes dans les fichiers
modifiés préservées, 23 004 nouveaux SIRET exactement (`verifications-ajouts.json`).

`verif_idf.py` relancé après intégration de main retourne **1**, uniquement pour la
régénération de `apres-3e/apres3e.json`. Le fichier servi est identique à main, comme
l'ensemble des fichiers `apres-3e/`, `formation/`, `aide/` et les scripts de génération
concernés. Aucune écriture dans ces dossiers.
Les 1 488 collèges constituent exactement le même ensemble mais sont réordonnés :
5 917 différences positionnelles. Les 102 autres écarts portent sur les durées :
68 champs `du`, 34 `duv`. Exemple : formation 42 « Bac pro cybersécurité, informatique
et réseaux, électronique », `duv` absent → 1 ; établissement 44 « Institut supérieur
de ressources informatiques », `du` absent → « 3 ans ». Le premier collège passe de
« Collège privé Oneschool Global Paris Campus » à « Annexe Oscar Romero du collège
La Salle - Saint-Rosaire de Sarcelles » par le tri. Voir `ecart-regeneration-apres3e.json`.
Ceci concorde avec les changements de durée/tri de PR 21 ; **non corrigé dans la 8.8**,
conformément à la demande de Naïm. Les pages affichées comparées sont toutes identiques.
Résultat exact : **« Autres pages Île-de-France identiques et contrat carte vérifié : non »**,
motif **« apres3e régénéré »**. Rapport intégral joint dans `verif-idf.txt` et collé dans la PR.

## Volume, durée et disque

Sirene national : **198 809 776 → 201 927 802 octets** (+3 118 026, soit +3,12 Mo décimaux).
Arbre de données final hors Git : **244240375 octets**. Tailles de chaque fichier et académie :
`tailles-fichiers.csv`, `bilan-academies.csv`, catalogues et manifestes du dépôt de données.

Pilote : 29 092 requêtes Recherche d'entreprises incluant les diagnostics, 99 min de
phases API ; fenêtre 12 h 35 min 58 s–14 h 42 min 31 s Paris (2 h 06, préparation et
pauses comprises, dont 13 h 53 min 46 s–14 h 13 min 10 s). Complément IDF : extraction
débutée à 15 h 50 min 31 s, 211,738 s de lecture Parquet ; 19 159 requêtes de vérification
individuelle entre 15 h 55 min 49 s et 17 h 01 min 24 s (1 h 05 min 35 s), dont cinq 429
repris avec succès ; sondage : 103 requêtes supplémentaires, ~21 s d'exécution.
Les transferts Parquet du complément représentent 1 212 249 165 octets réseau pour
193 952 008 octets d'extraits locaux. Ils sont distincts des requêtes de l'API Recherche.
Extraits contrôlés puis effacés, SHA/tailles conservés dans `extraits-nettoyes.json`.
Arrêt explicite sous 2 Go, reprise après libération d'espace : cette pause de préparation
des PR ne fait pas partie de la durée de collecte. Aucune collecte hors IDF lancée.

## Relecture

Deux PR liées, données et code, sans fusion ni publication. Le statut CI doit être vérifié
sur le dernier commit avant livraison ; il est consultable sur la PR, pas affirmé par ce
rapport local. Restent hors périmètre : autre France, évolution du classement, fichiers
historiques d'orientation, tâche mensuelle installée, licences et historique Git.
