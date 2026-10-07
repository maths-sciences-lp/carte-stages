# Audit RGAA 4.1.2 — bilan des corrections du 7 octobre 2026

## Portée et limite de validité

Ce travail examine les 106 critères sur l’échantillon décrit dans [l’état initial](avant.md), enregistré avant les corrections. Le détail ci-dessous distingue les constats techniques établis des vérifications de restitution vocale incomplètes. **Ce n’est pas une certification de conformité. La déclaration conserve l’état « non conforme » en l’absence d’un audit de restitution complet.** Les critères dont la restitution vocale n’a pas été validée restent NC par prudence, sans les retirer du dénominateur. Aucun score axe n’est présenté comme un taux RGAA.

VoiceOver, déjà intégré à macOS, a été activé puis désactivé dans les réglages. Safari expose les noms des champs, les boutons, le résumé de choix d’académie et les liens « nouvel onglet ». Toutefois les commandes du contrôle natif n’ont pas permis de valider fiablement la restitution vocale et les parcours VoiceOver complets. Il ne serait pas exact de les déclarer réussis. Aucun test NVDA/JAWS ni test sur téléphone physique n’a été réalisé. Les formats 320/375 px sont des fenêtres de navigateur de bureau.

## Comptage exact de la grille

Un critère est NC dès qu’un élément applicable de l’échantillon échoue. Les NA sont exclus. Les vérifications vocales non validées sont conservées NC. Les fractions ci-dessous sont exactes, sans arrondi.

- **Avant, après adjudication** : 39 C, 24 NC, 43 NA ; 39/63 × 100 = **1300/21 %** (environ 61,9 %). Ce comptage de constats ne remplace pas le taux d’un audit RGAA complet.
- **Après** : 50 C, 14 NC, 42 NA ; 50/64 × 100 = **78,125 %** (625/8 %, valeur exacte). Ce comptage de constats ne remplace pas le taux d’un audit RGAA complet.

L’adjudication de l’état initial corrige quatre classifications de la grille de travail, sans prétendre qu’il s’agit d’améliorations du code : titres nationaux déjà corrects (8.6), pertinence des étiquettes existantes (11.2), emojis accompagnés de texte (13.5), finalité des champs adresse/ville incorrectement marquée conforme (11.13). L’état initial figé reste disponible pour la traçabilité.

## Corrections et vérifications

- Labels visibles, contours des champs et du focus, contrastes des textes secondaires.
- Navigation par Tab/Maj+Tab, flèches, Entrée, Échap ; focus maintenu lors des reconstructions et des choix.
- États développés des lycées, régions de statut, nom des marqueurs, alternative Liste à la carte.
- Repères structurels, lien d’évitement, noms contextualisés des liens externes et indicateur de nouvel onglet.
- Cinq transcriptions sous les vidéos, sans modifier les médias ; prise en compte de la réduction des mouvements.
- Gabarits de génération mis à jour pour conserver les corrections lors des prochaines mises à jour.

Aucune donnée, adresse métier, redirection de classe, licence ou valeur DV modifiée. La FAQ et source/README.md restent inchangés ; leurs propositions sont dans la PR.

Environnement : macOS 15.7.4 ; Chromium 147.0.7727.15 fourni avec Playwright ; axe-core 4.14.0 local ; Safari 18.6 et VoiceOver tentés avec les limites précisées ci-dessus. HTML, CSS, JavaScript, SVG, Leaflet 1.9.4, Leaflet.markercluster 1.5.3 et lecteurs vidéo HTML natifs. Aucun nouvel outil d’audit n’est chargé en production. Tests sans CSS, zoom 200 %, espacements du texte et parcours clavier documentés dans les fichiers de résultats.

Résultats finaux : 44 états axe examinés, aucune erreur JavaScript/console et aucune violation axe hors FAQ. Le détail des lycées inclut des badges Public et Privé sous contrat. Parcours clavier validés sur les quatre outils ; sélection manuelle de Martinique et retour « changer ». Localisation simulée à Lyon et choix d’une ville avec une réponse BAN simulée : retour du focus vérifié. Douze adresses nationales complémentaires (quatre académies sur les trois outils) ouvertes sans erreur.

Le contrôle de non-régression régénère les quatre JSON par défaut : identiques octet par octet. Les 20 adresses vérifiées conservent leurs résultats et états de champs. Le texte brut change volontairement avec les libellés, l’évitement, le lien Accessibilité et les indications ajoutées ; le mode `--accessibilite` ne prétend pas à une identité visuelle. Voir [résumé du contrôle](verif-idf.txt).

Captures à 375 px : [focus et contraste](captures/focus-contraste.png), [choix d’académie](captures/question.png), [transcription](captures/transcription.png), [déclaration](captures/declaration.png).

## Non-conformités restantes et alternatives

- **4.3** : Vidéos : pas de piste de sous-titres séparée ; équivalence de toute la bande sonore non validée. Les textes incrustés ne suffisent pas à conclure. Transcriptions disponibles.
- **4.5** : Vidéos : pas de piste d’audiodescription ; les actions visuelles sont proposées en transcription texte. Restitution synchronisée non validée.
- **4.13** : Lecteur HTML natif identifié et commandes clavier testées ; compatibilité vocale complète non validée dans la présente session.
- **7.1** : Noms, états et relations ARIA corrigés, mais restitution VoiceOver des composants dynamiques non validée de bout en bout.
- **7.5** : Régions role=status/aria-live ajoutées pour résultats et suggestions ; annonces vocales réelles non validées de bout en bout.
- **8.2** : FAQ inchangée : éléments li hors ul/ol.
- **9.2** : FAQ inchangée : en-tête et pied de page sans repères structurels dédiés.
- **9.3** : FAQ inchangée : trois éléments li isolés.
- **10.11** : FAQ inchangée : débordement horizontal à 320 px.
- **10.12** : FAQ inchangée : débordement avec les espacements de texte du RGAA.
- **12.1** : Le site ne dispose pas encore d’un deuxième système transversal de navigation couvrant toutes les pages.
- **12.6** : FAQ inchangée : repères incomplets pour atteindre/éviter les zones récurrentes.
- **12.7** : Lien d’évitement ajouté aux pages corrigées, absent de la FAQ conservée inchangée.
- **13.3** : PDF de présentation non balisé (pdfinfo : Tagged: no), sans version HTML intégrale équivalente. Contact proposé pour demander une version accessible.

Aucune dérogation pour charge disproportionnée ni exemption n’est revendiquée. Une contrainte de périmètre (FAQ inchangée) est une non-conformité restante, pas une dérogation juridique.

## Grille complète

C = conforme sur les vérifications décrites ; NC = non conforme ou restitution non validée ; NA = non applicable.

| Critère | Avant revu | Après | Justification après |
|---|---|---|---|
|1.1|C|C|Images : logo SVG décoratif aria-hidden, tuiles de carte alt vide ; marqueurs possèdent une alternative (pertinence traitée en 1.3).|
|1.2|C|C|SVG du logo masqué ; tuiles de carte décoratives avec alt vide. Emojis traités en 13.5.|
|1.3|NC|C|Marqueurs des trois outils nommés avec le nom réel du lieu ; alternative Liste maintenue.|
|1.4|NA|NA|Aucun CAPTCHA ou image-test.|
|1.5|NA|NA|Aucun CAPTCHA.|
|1.6|C|C|Listes textuelles présentent les lieux et adresses figurant sur la carte.|
|1.7|C|C|Listes issues des mêmes objets que les marqueurs ; données et adresses disponibles.|
|1.8|NA|NA|Pas de texte essentiel sous forme d’image hors cartes et médias traités séparément.|
|1.9|NA|NA|Pas de légende d’image indépendante.|
|2.1|NA|NA|Aucun cadre iframe/frame.|
|2.2|NA|NA|Aucun cadre.|
|3.1|C|C|Étiquettes Public/Privé, noms des domaines et états aria-pressed doublent la couleur.|
|3.2|NC|C|Texte secondaire #596477 ; axe ne relève plus de contraste insuffisant sur les états testés.|
|3.3|NC|C|Contours des champs #778397, focus #15314f et anneau blanc, y compris le sélecteur national.|
|4.1|NC|C|Cinq transcriptions textuelles repliables immédiatement sous les vidéos ; même transcription signalée pour la version horizontale.|
|4.2|NA|C|Transcriptions confrontées aux captures successives des vidéos : étapes, commandes et informations essentielles reprises. Aucun texte ASR non vérifié utilisé.|
|4.3|NC|NC|Vidéos : pas de piste de sous-titres séparée ; équivalence de toute la bande sonore non validée. Les textes incrustés ne suffisent pas à conclure. Transcriptions disponibles.|
|4.4|NA|NA|Pas de piste de sous-titres.|
|4.5|NC|NC|Vidéos : pas de piste d’audiodescription ; les actions visuelles sont proposées en transcription texte. Restitution synchronisée non validée.|
|4.6|NA|NA|Pas de piste d’audiodescription.|
|4.7|C|C|demo/ : titres immédiatement avant les tutoriels et introduction du film.|
|4.8|NA|NA|Pas de média non temporel embarqué de type objet/canvas porteur d’information sans liste équivalente. Cartes traitées en 7.|
|4.9|NA|NA|Voir 4.8.|
|4.10|NA|NA|Aucun son démarré automatiquement.|
|4.11|C|C|Lecteurs HTML video controls : commandes natives accessibles au clavier ; confirmation VoiceOver distincte en 4.13.|
|4.12|NA|NA|Voir 4.8.|
|4.13|NC|NC|Lecteur HTML natif identifié et commandes clavier testées ; compatibilité vocale complète non validée dans la présente session.|
|5.1|NA|NA|Aucun tableau de données complexe.|
|5.2|NA|NA|Aucun tableau complexe.|
|5.3|NA|NA|Aucun tableau de mise en forme.|
|5.4|NA|NA|Aucun tableau de données.|
|5.5|NA|NA|Aucun tableau de données.|
|5.6|NA|NA|Aucun tableau de données.|
|5.7|NA|NA|Aucun tableau de données.|
|5.8|NA|NA|Aucun tableau de mise en forme.|
|6.1|C|C|Liens dans leur contexte de carte de résultat ; noms des ressources en pied de page. Ajout de noms de lieux prévu pour améliorer la liste de liens.|
|6.2|C|C|Aucun lien vide détecté sur les états audités.|
|7.1|NC|NC|Noms, états et relations ARIA corrigés, mais restitution VoiceOver des composants dynamiques non validée de bout en bout.|
|7.2|NA|NA|Aucune alternative séparée à un script non compatible ; liste et carte sont deux vues du même jeu de données.|
|7.3|NC|C|Parcours clavier des quatre outils, listes/cartes et choix/changement d’académie exécutés ; commandes natives conservées.|
|7.4|C|C|Changements de vue déclenchés par choix explicite ; pas de navigation au focus.|
|7.5|NC|NC|Régions role=status/aria-live ajoutées pour résultats et suggestions ; annonces vocales réelles non validées de bout en bout.|
|8.1|C|C|Doctype HTML sur toutes les pages de l’échantillon.|
|8.2|NC|NC|FAQ inchangée : éléments li hors ul/ol.|
|8.3|C|C|html lang=fr présent.|
|8.4|C|C|Contenu français, code fr pertinent.|
|8.5|C|C|title présent sur chaque page.|
|8.6|C|C|Les callbacks nationaux définissent bien le titre avec le nom de l’académie ; titre générique pertinent avant le choix.|
|8.7|NA|NA|Pas de passage en langue étrangère hors noms propres et noms de diplômes.|
|8.8|NA|NA|Aucun changement de langue à baliser.|
|8.9|C|C|Sections et paragraphes portent du contenu ; CSS assure la mise en forme.|
|8.10|NA|NA|Aucun changement de direction de lecture.|
|9.1|NC|C|Titres h3 pour les entreprises ; titres h1/h2/h3 des autres outils conservés.|
|9.2|NC|NC|FAQ inchangée : en-tête et pied de page sans repères structurels dédiés.|
|9.3|NC|NC|FAQ inchangée : trois éléments li isolés.|
|9.4|NA|NA|Aucune citation longue nécessitant un balisage de citation.|
|10.1|C|C|Présentation assurée par CSS, sans tableau de mise en forme.|
|10.2|C|C|Contenus textuels présents dans le DOM ; cartes disposent des listes.|
|10.3|C|C|Ordre source : choix, départ, résultats puis sources ; listes intelligibles sans styles.|
|10.4|C|C|Zoom de mise en page 200 % sur les huit pages types, pas de débordement global ; captures à contrôler visuellement.|
|10.5|C|C|Couleurs de texte et fonds définis dans les styles des cartes/boutons/pages.|
|10.6|C|C|Liens textuels soulignés ; boutons et cartes de navigation identifiables par leur forme et contexte.|
|10.7|NC|C|Contour de focus visible renforcé sur les pages corrigées ; boutons et résumés natifs de la FAQ conservent leur contour navigateur.|
|10.8|C|C|hidden utilisé pour les vues inactives, CSS display:none pour les vues mobiles masquées.|
|10.9|C|C|Consignes nomment les commandes ; numéros d’étapes accompagnés de titres.|
|10.10|NA|NA|Pas d’instruction fondée seulement sur la forme, la taille ou la position.|
|10.11|NC|NC|FAQ inchangée : débordement horizontal à 320 px.|
|10.12|NC|NC|FAQ inchangée : débordement avec les espacements de texte du RGAA.|
|10.13|NA|NA|Pas de contenu additionnel personnalisé au survol ou au focus.|
|10.14|NA|NA|Pas de contenu additionnel affiché par CSS uniquement.|
|11.1|NC|C|Labels visibles et liés aux champs, y compris les champs clonés par les adaptateurs nationaux.|
|11.2|C|C|Les étiquettes existantes sont pertinentes ; l’absence d’étiquette relève de 11.1.|
|11.3|C|C|Champs collège/adresse cohérents entre outils, académie commune.|
|11.4|C|C|Étiquettes existantes accolées aux champs (ville/lycée). Absences en 11.1.|
|11.5|NA|NA|Champs de recherche indépendants, pas de groupes de cases ou de coordonnées à regrouper.|
|11.6|NA|NA|Aucun regroupement nécessaire.|
|11.7|NA|NA|Aucun regroupement nécessaire.|
|11.8|NA|NA|Liste de lycées homogène, pas de catégories à regrouper.|
|11.9|C|C|Boutons de recherche, choix, localisation, filtres : intitulés décrivent l’action.|
|11.10|NA|NA|Aucun champ obligatoire ni format imposé ; recherches libres.|
|11.11|NA|NA|Aucun contrôle de saisie de format.|
|11.12|NA|NA|Aucun formulaire à conséquences juridiques ou financières, aucun examen ni modification de données serveur.|
|11.13|NC|C|Adresse autocomplete=street-address ; ville autocomplete=address-level2.|
|12.1|NC|NC|Le site ne dispose pas encore d’un deuxième système transversal de navigation couvrant toutes les pages.|
|12.2|C|C|Lien de retour en haut, liens transversaux et sources en bas.|
|12.3|NA|NA|Pas de page intitulée plan du site.|
|12.4|NA|NA|Pas de plan du site.|
|12.5|NA|NA|Pas de moteur de recherche transversal au site.|
|12.6|NC|NC|FAQ inchangée : repères incomplets pour atteindre/éviter les zones récurrentes.|
|12.7|NC|NC|Lien d’évitement ajouté aux pages corrigées, absent de la FAQ conservée inchangée.|
|12.8|NC|C|Focus rendu au champ après une suggestion, au filtre remplacé, au premier nouveau résultat après « plus », au titre après le choix d’académie.|
|12.9|C|C|Dialogue initial fermé par Échap ; aucune capture permanente de Tab dans les scripts.|
|12.10|NA|NA|Pas de raccourci à caractère imprimable défini par le site ; commandes natives des lecteurs traitées en 4.|
|12.11|C|C|Suggestions faites de boutons tabulables ; listes supplémentaires sur activation. Pertes de focus traitées en 12.8.|
|13.1|NA|NA|Aucune limite de temps interrompant une tâche ; temporisations réseau ne font pas perdre les saisies.|
|13.2|C|C|Liens target=_blank déclenchés par action explicite uniquement ; signalement supplémentaire prévu.|
|13.3|NC|NC|PDF de présentation non balisé (pdfinfo : Tagged: no), sans version HTML intégrale équivalente. Contact proposé pour demander une version accessible.|
|13.4|NA|NA|Pas de version accessible du PDF identifiée avant correction.|
|13.5|C|C|Emojis accompagnés d’un intitulé compréhensible ; masquage décoratif ajouté en amélioration.|
|13.6|C|C|Symboles signifiants accompagnés de texte (distance, internat, téléphone).|
|13.7|C|C|Pas de clignotement programmé ni animation de flash dans les interfaces.|
|13.8|C|C|Vidéos sur commande, pause disponible ; pas de carrousel automatique.|
|13.9|C|C|Aucun verrouillage portrait/paysage dans les pages.|
|13.10|C|C|Carte : boutons +/−, clavier et vue Liste pour les gestes de déplacement/zoom.|
|13.11|C|C|Actions via click, activation au relâchement ; déplacement de carte réversible.|
|13.12|NA|NA|Pas de commande par mouvement de l’appareil.|

## Sources de méthode

- [Critères et tests RGAA 4.1.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/).
- [Environnement de test](https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/).
- [Modèle de déclaration](https://accessibilite.numerique.gouv.fr/obligations/declaration-accessibilite/).

Consultés le 7 octobre 2026. Le contrôle Île-de-France est conservé séparément ; son mode accessibilité exclut uniquement les ajouts identifiés de navigation et de libellés, conserve les textes bruts et compare toujours les données et les états des champs.
