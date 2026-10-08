# Mission 8.5 — carte historique et source nationale commune

Les 180 clés distribuées restent résolues, avec les mêmes types d’entreprises,
le même ordre des domaines et les 469 points de départ historiques. La recherche
propose aussi les 252 CAP/bacs pro nationaux, 14 familles de seconde pro et 2 BMA.
Les données Sirene du 8 octobre 2026 et les indications LBA nationales sont
chargées par `stage/donnees.js`, partagé par la carte historique et les pages nationales.

## Adresses et comportement conservés

`/`, `/henaff/`, `/tne`, `/mnb`, `/mama`, `/iccer`, `/mee`, `/tma`, `/era`, `/eeb`,
`/geometre`, `/mit`, `/sdg`, `/ebeniste`, `/bma-ebeniste`, `/bma-signaletique`, `/ma`.
Les fichiers de redirection, leurs variantes avec `/` ou `/index.html`, les liens
`#f=…`, `#ly=…`, `#d=…` et leurs combinaisons restent inchangés. Le paramètre
historique `lycee=latitude,longitude` reste reconnu. La formation prime sur le
domaine lorsqu’ils sont combinés, comme avant.

`correspondances-180.csv` documente les 180 résolutions. Les quatre alias de
`stage/aliases-idf.json` reproduisent la **première option** trouvée par le code
historique quand deux options partageaient une clé tronquée. Leur ancienne clé
reste dans le hash et dans l’événement GoatCounter. Les autres options sont
sélectionnables séparément depuis la recherche nationale. Les autres noms
GoatCounter, les boutons, distances, filtres, badges et liens LBA sont conservés.

La page `/` conserve son introduction francilienne et « Tu habites ailleurs en
France ? Indique ta ville », sans sélecteur d’académie. Maison est toujours
mémorisée, dans un try/catch ; `data/lycees.json` reste la liste de départ.
Les marqueurs sont créés seulement pour les résultats visibles ; aucun plafond
n’est ajouté à la carte historique. Le plafond national existant de 1 500
marqueurs reste inchangé, avec la liste complète et son avertissement.

## Catalogue léger et frontières

Un catalogue national léger commun évite 30 duplications : formations,
domaines, rectangles géographiques, version des fichiers de lycées et des
manifestes départementaux. Le détail des fichiers Sirene attend le choix d’une
formation ; LBA aussi. Le catalogue complet reste disponible pour les scripts
et les anciennes versions du site pendant la transition.

| Catalogue | Avant (octets) | Après (octets) | Gzip avant → après |
|---|---:|---:|---:|
| Pages nationales | 1 694 919 | 100 437 | 580 558 → 27 151 |
| Catalogue historique IDF → nouveau catalogue IDF | 51 205 | 76 243 | 9 778 → 15 977 |

Le catalogue IDF augmente de 25 Ko par rapport à l’ancien petit index car il
contient toutes les formations et 16 départements. Il évite de charger les
1,69 Mo du catalogue national complet. Gzip mesuré localement, pas une mesure
du transfert HTTP de GitHub Pages. Aucun fichier Sirene, manifeste ou LBA n’est
chargé sur `/` sans choix de formation/domaine (un hash est un choix explicite).

Le catalogue IDF couvre les huit départements franciliens et 02, 10, 27, 28,
45, 51, 60, 89. Le rayon charge les départements dont le rectangle intersecte
le cercle, puis filtre à la distance exacte. Le même principe s’applique aux
101 départements sur les pages nationales. Le bouton « Toutes » de `/` garde
l’Île-de-France entière ; « Toute la région » national garde la région choisie.

Tests : Hénaff `0932119Y`, ICCER, 5 km : **353 entreprises du 75** ; Eu,
Normandie, CAP cuisine, 5 km : **28 entreprises du 80** (académie Amiens) ;
point près d’Égreville, CAP cuisine, 5 km : **1 entreprise du 45**. Aucun
filtrage par académie n’exclut ces résultats.

## Lycées

2 487 UAI initiaux conservés, 699 UAI ajoutés : **3 186 UAI**. Source Onisep
605340ddc19a9, empreinte et liens de chaque établissement dans le rapport de la
PR de données. Le recomptage donne 768 absents, et non 764. Parmi eux, 66 UAI de
collectivités hors des 30 académies, un à Andorre et un à Monaco restent hors
périmètre, conformément à la décision de Naïm. Les deux antennes du GRETA Réunion
(UAI 9741070V) sont différées avec son accord. L’antenne Plabennec de 0291604L est
confirmée par l’annuaire officiel ; ses coordonnées retenues viennent d’Onisep.
55 lignes sans UAI sont signalées sans identifiant inventé. 47 des ajouts sont
en Île-de-France (catalogue national) ; les 469 lycées historiques de `/` ne changent pas.

## Entreprises : comparaison des instantanés

IDF : **316 998 → 325 236 SIRET uniques** (+8 238), 86 → 122 types d’entreprises.
Les correspondances des 180 anciennes clés n’ont pas changé. Pour comparer,
« IDF » signifie exactement les huit départements, sans département limitrophe.
Le dédoublonnage garde la première occurrence, comme le navigateur.

| Adresse / formation | IDF avant → après | À 5 km d’Hénaff avant → après |
|---|---:|---:|
| `/tne` | 16 711 → 16 727 | 1 484 → 1 468 |
| `/mnb` | 36 329 → 36 185 | 3 763 → 3 773 |
| `/mama` | 5 555 → 5 554 | 631 → 628 |
| `/iccer` | 8 554 → 8 574 | 782 → 777 |
| `/mee` | 8 554 → 8 574 | 782 → 777 |
| `/tma` | 5 296 → 5 297 | 603 → 601 |
| `/era` | 5 296 → 5 297 | 603 → 601 |
| `/eeb` | 34 517 → 34 368 | 3 674 → 3 683 |
| `/geometre` | 19 460 → 19 326 | 1 382 → 1 394 |
| `/mit` | 8 189 → 8 223 | 758 → 758 |
| `/sdg` | 5 621 → 5 627 | 787 → 786 |
| `/ebeniste` | 5 296 → 5 297 | 603 → 601 |
| `/bma-ebeniste` | 5 555 → 5 554 | 631 → 628 |
| `/bma-signaletique` | 5 621 → 5 627 | 787 → 786 |
| `/ma` | 5 296 → 5 297 | 603 → 601 |
| `/#f=cap-cuisine` | 41 297 → 41 321 | 5 237 → 5 235 |
| `/#f=cap-boulanger` | 12 880 → 12 854 | 1 786 → 1 782 |
| `/#f=cap-patissier` | 35 632 → 35 613 | 4 593 → 4 585 |
| `/#f=cap-accompagnant-educatif-petite-enfance` | 20 738 → 20 714 | 1 858 → 1 885 |
| `/#f=bac-pro-accompagnement-soins-et-services-a-la-personne` | 10 575 → 10 730 | 1 015 → 1 027 |

`comptages.json` donne, pour chaque ligne et les deux rayons, le nombre d’entrées,
de sorties et chaque SIRET retiré, ainsi que ses secteurs nationaux lorsqu’il est
reclassé. Les baisses ne sont donc pas assimilées à des fermetures.

**Limite importante de la source, à relire avant fusion :** 1 045 SIRET des vingt
formations sont absents du relevé départemental. Le contrôle individuel par l’API
le 8 octobre trouve **79 fermés, 2 en diffusion restreinte et 964 toujours actifs**.
Les observations figurent dans `entreprises-api.json` (URL et champs minimaux,
sans contacts). Une réponse 429 a été reprise ; aucun échec ne subsiste.
L’état constaté ne prouve pas la date de fermeture entre les deux collectes.

Pour ICCER à 5 km : 782 → 777 = 782 − 10 + 5. Les dix retraits correspondent
à deux établissements déclarés fermés et huit encore actifs par SIRET, absents
du relevé départemental. Les requêtes départementales EDF reproduites avec les
paramètres historiques puis nationaux renvoient la même liste de six sites,
dont trois actifs, sans les cinq sites EDF retirés de ce rayon. Cela écarte le
paramètre `minimal` comme explication pour cet exemple. Preuve dans
`comparaison-requetes.json`. **La raison interne de cette différence de réponses
API n’est pas établie** : aucun changement d’activité ou fermeture n’est inventé.
Les fichiers Sirene nationaux validés ne sont pas retouchés dans cette mission.

## Vérification et entretien

`verif_idf.py --donnees-nationales /copie/donnees` conserve les comparaisons
strictes des autres pages et des 175 fichiers historiques, puis vérifie le
contrat de la carte avec les données de la PR servies localement. Le relevé des
62 parcours à 320/375 px, 180 clés, 469 UAI, frontières et mesures CPU ×4 est
dans `carte-contrat.json`. Maison, stockage refusé, reprise HTTP 503, badges LBA
et clavier sont testés. Axe ne relève pas de violation WCAG A/AA sur le parcours
testé : cela ne vaut pas audit RGAA complet.

La FAQ est alignée sur les 252 diplômes, les 3 186 établissements nationaux et le complément Onisep ; son adresse ne change pas.

La déclaration `/accessibilite/` n’est pas modifiée. Les parcours et composants
accessibles restent les mêmes ; son inventaire de pages testées pourra mentionner
cette vérification à la prochaine révision, sans annoncer une nouvelle conformité.

`data/` et `data/lba/` sont conservés intégralement comme instantané historique.
Seul `data/lycees.json` reste lu par la carte. Pas de suppression, pas de nouvelle
collecte Sirene, pas de réécriture d’historique, pas de changement de DV/licences.
La proposition `source/maj-lba.sh` prépare désormais seulement les fichiers LBA
nationaux ; le remplacement conserve les derniers fichiers valides en cas
d’échec. La tâche installée n’a pas été modifiée ni exécutée. À noter : le lanceur
qui récupère le script sur main prendra cette évolution après validation/fusion.

La PR 15 de surveillance nocturne a été intégrée pendant le travail (base
5d1f8a3, avec la nouvelle page Hénaff de la PR 16). Sa vérification de fraîcheur de l’ancien `data/lba` est remplacée par
la vérification de l’unique export national, pour éviter une fausse alerte sur
l’archive. Les deux catalogues légers sont désormais surveillés aussi.

Ordre de validation proposé : PR de données d’abord, attendre la disponibilité
publique des catalogues et manifestes, puis PR de code. Sans les nouveaux fichiers,
le code affiche une erreur récupérable au lieu de revenir silencieusement à une
autre source. Pour revenir en arrière, revert du commit de code : tous les anciens
fichiers restent présents. Les deux PR sont non fusionnées et non déployées.

## Mesures locales à 375 px, CPU ×4

| Parcours | Avant (ms) | Après (ms) |
|---|---:|---:|
| / | 339 | 319 |
| /iccer | 515 | 437 |
| /iccer : Toute la région (bouton Toutes) | 798 | 1243 |

Une mesure par parcours, cache navigateur neuf à chaque ouverture, fichiers de données servis localement. La ligne « Toute la région » mesure le clic après ouverture d’ICCER. Ce sont des mesures de calcul/rendu et de chargement local, pas une promesse de temps sur réseau mobile. Les variations entre exécutions rendent les petits écarts non significatifs.
