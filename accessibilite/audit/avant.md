# Audit initial — 7 octobre 2026

État figé avant toute correction, commit 936b2d8. Référentiel RGAA 4.1.2 (106 critères).

**Grille de travail : le taux est provisoire tant que la vérification VoiceOver, les médias et les documents ne sont pas terminés. Les points non établis ne sont pas présentés comme conformes.**

Échantillon : accueil/, / (dialogue, recherche cuisine, départ lycée, liste, carte), henaff/, iccer, apres-3e/#cuisine, formation/#eeb, aide/#mda, les trois entrées france/ et Lyon, faq/ dépliée, demo/. Deux largeurs : 375 et 320 px. Zoom 200 % et espacement du texte sur huit pages types.

Première passe : axe-core local, Chromium, observations de la structure et du code, activation au clavier. Les champs placeholder seul passent certains tests axe mais restent non conformes au RGAA. Résultats automatiques conservés dans avant-axe.json ; observations clavier/espacement dans avant-manuel.json.

Comptage initial : {'C': 37, 'NC': 26, 'NA': 43}. Formule : C / (106 − NA) × 100. Ne pas confondre ce comptage provisoire avec une déclaration de conformité définitive.

|Critère|État avant|Motif et emplacement|
|---|---|---|
|1.1|C|Images : logo SVG décoratif aria-hidden, tuiles de carte alt vide ; marqueurs possèdent une alternative (pertinence traitée en 1.3).|
|1.2|C|SVG du logo masqué ; tuiles de carte décoratives avec alt vide. Emojis traités en 13.5.|
|1.3|NC|Cartes des trois outils : marqueurs Leaflet nommés « Marker », sans nom du lieu.|
|1.4|NA|Aucun CAPTCHA ou image-test.|
|1.5|NA|Aucun CAPTCHA.|
|1.6|C|Listes textuelles présentent les lieux et adresses figurant sur la carte.|
|1.7|C|Listes issues des mêmes objets que les marqueurs ; données et adresses disponibles.|
|1.8|NA|Pas de texte essentiel sous forme d’image hors cartes et médias traités séparément.|
|1.9|NA|Pas de légende d’image indépendante.|
|2.1|NA|Aucun cadre iframe/frame.|
|2.2|NA|Aucun cadre.|
|3.1|C|Étiquettes Public/Privé, noms des domaines et états aria-pressed doublent la couleur.|
|3.2|NC|Après le collège, Après le lycée, Aide : #667085 sur #eef2f6, ratio axe 4,42:1 (<4,5).|
|3.3|NC|Bordures des champs #e4e9ee sur blanc et fond gris insuffisantes pour identifier les zones de saisie.|
|4.1|NC|demo/ : aucune transcription textuelle sous les cinq vidéos.|
|4.2|NA|Pas de transcription proposée avant correction.|
|4.3|NC|demo/ : aucune piste de sous-titres synchronisés fournie ; les légendes incrustées demandent une vérification intégrale.|
|4.4|NA|Pas de piste de sous-titres.|
|4.5|NC|demo/ : restitution de toutes les actions visuelles par la narration non encore établie ; ne pas déclarer conforme sans examen.|
|4.6|NA|Pas de piste d’audiodescription.|
|4.7|C|demo/ : titres immédiatement avant les tutoriels et introduction du film.|
|4.8|NA|Pas de média non temporel embarqué de type objet/canvas porteur d’information sans liste équivalente. Cartes traitées en 7.|
|4.9|NA|Voir 4.8.|
|4.10|NA|Aucun son démarré automatiquement.|
|4.11|C|Lecteurs HTML video controls : commandes natives accessibles au clavier ; confirmation VoiceOver distincte en 4.13.|
|4.12|NA|Voir 4.8.|
|4.13|NC|Compatibilité des lecteurs natifs avec VoiceOver à terminer ; conformité non établie.|
|5.1|NA|Aucun tableau de données complexe.|
|5.2|NA|Aucun tableau complexe.|
|5.3|NA|Aucun tableau de mise en forme.|
|5.4|NA|Aucun tableau de données.|
|5.5|NA|Aucun tableau de données.|
|5.6|NA|Aucun tableau de données.|
|5.7|NA|Aucun tableau de données.|
|5.8|NA|Aucun tableau de mise en forme.|
|6.1|C|Liens dans leur contexte de carte de résultat ; noms des ressources en pied de page. Ajout de noms de lieux prévu pour améliorer la liste de liens.|
|6.2|C|Aucun lien vide détecté sur les états audités.|
|7.1|NC|Boutons Voir les lycées sans aria-expanded ; suggestions non annoncées ; marqueurs génériques.|
|7.2|NA|Aucune alternative séparée à un script non compatible ; liste et carte sont deux vues du même jeu de données.|
|7.3|NC|Le choix d’un domaine reconstruit le bouton actif et renvoie le focus au body (trois outils). Choix d’académie masque le bouton actif.|
|7.4|C|Changements de vue déclenchés par choix explicite ; pas de navigation au focus.|
|7.5|NC|Compteurs, suggestions et erreurs des outils sans région de statut (hors sélecteur d’académie).|
|8.1|C|Doctype HTML sur toutes les pages de l’échantillon.|
|8.2|NC|FAQ : trois li hors ul/ol (premiers vœux, Parcoursup, lieux d’aide), axe listitem.|
|8.3|C|html lang=fr présent.|
|8.4|C|Contenu français, code fr pertinent.|
|8.5|C|title présent sur chaque page.|
|8.6|NC|Le chargement national remplace le titre par le titre générique du moteur ; académie absente du title.|
|8.7|NA|Pas de passage en langue étrangère hors noms propres et noms de diplômes.|
|8.8|NA|Aucun changement de langue à baliser.|
|8.9|C|Sections et paragraphes portent du contenu ; CSS assure la mise en forme.|
|8.10|NA|Aucun changement de direction de lecture.|
|9.1|NC|Stage : noms des entreprises dans div.nm, pas de titres de résultats.|
|9.2|NC|Stage : aucun main ; autres pages : lien d’en-tête hors header ; pieds de page statiques non structurés.|
|9.3|NC|FAQ : li isolés hors liste.|
|9.4|NA|Aucune citation longue nécessitant un balisage de citation.|
|10.1|C|Présentation assurée par CSS, sans tableau de mise en forme.|
|10.2|C|Contenus textuels présents dans le DOM ; cartes disposent des listes.|
|10.3|C|Ordre source : choix, départ, résultats puis sources ; listes intelligibles sans styles.|
|10.4|C|Zoom de mise en page 200 % sur les huit pages types, pas de débordement global ; captures à contrôler visuellement.|
|10.5|C|Couleurs de texte et fonds définis dans les styles des cartes/boutons/pages.|
|10.6|C|Liens textuels soulignés ; boutons et cartes de navigation identifiables par leur forme et contexte.|
|10.7|NC|Stage : .sug button:focus supprime outline, seul fond gris très clair ; contours de focus non uniformes.|
|10.8|C|hidden utilisé pour les vues inactives, CSS display:none pour les vues mobiles masquées.|
|10.9|C|Consignes nomment les commandes ; numéros d’étapes accompagnés de titres.|
|10.10|NA|Pas d’instruction fondée seulement sur la forme, la taille ou la position.|
|10.11|NC|FAQ : débordement horizontal à 320 px, notamment lien long.|
|10.12|NC|FAQ : largeur 394 px pour fenêtre 320 px avec espacements RGAA.|
|10.13|NA|Pas de contenu additionnel personnalisé au survol ou au focus.|
|10.14|NA|Pas de contenu additionnel affiché par CSS uniquement.|
|11.1|NC|Après le collège/Aide : champs q/col/adr avec placeholder seul ; Formation : adresse sans étiquette.|
|11.2|NC|Certains libellés ne persistent pas après saisie ; voir 11.1.|
|11.3|C|Champs collège/adresse cohérents entre outils, académie commune.|
|11.4|C|Étiquettes existantes accolées aux champs (ville/lycée). Absences en 11.1.|
|11.5|NA|Champs de recherche indépendants, pas de groupes de cases ou de coordonnées à regrouper.|
|11.6|NA|Aucun regroupement nécessaire.|
|11.7|NA|Aucun regroupement nécessaire.|
|11.8|NA|Liste de lycées homogène, pas de catégories à regrouper.|
|11.9|C|Boutons de recherche, choix, localisation, filtres : intitulés décrivent l’action.|
|11.10|NA|Aucun champ obligatoire ni format imposé ; recherches libres.|
|11.11|NA|Aucun contrôle de saisie de format.|
|11.12|NA|Aucun formulaire à conséquences juridiques ou financières, aucun examen ni modification de données serveur.|
|11.13|C|Champs adresse autocomplete=street-address ; ville du sélecteur à compléter pour address-level2.|
|12.1|NC|Navigation transversale essentiellement par liens ; pas de second système couvrant tout le site.|
|12.2|C|Lien de retour en haut, liens transversaux et sources en bas.|
|12.3|NA|Pas de page intitulée plan du site.|
|12.4|NA|Pas de plan du site.|
|12.5|NA|Pas de moteur de recherche transversal au site.|
|12.6|NC|Repères de navigation/header/footer/main incomplets.|
|12.7|NC|Aucun lien d’évitement vers le contenu principal.|
|12.8|NC|Focus perdu après reconstruction des boutons, et masqué après choix d’académie.|
|12.9|C|Dialogue initial fermé par Échap ; aucune capture permanente de Tab dans les scripts.|
|12.10|NA|Pas de raccourci à caractère imprimable défini par le site ; commandes natives des lecteurs traitées en 4.|
|12.11|C|Suggestions faites de boutons tabulables ; listes supplémentaires sur activation. Pertes de focus traitées en 12.8.|
|13.1|NA|Aucune limite de temps interrompant une tâche ; temporisations réseau ne font pas perdre les saisies.|
|13.2|C|Liens target=_blank déclenchés par action explicite uniquement ; signalement supplémentaire prévu.|
|13.3|NC|demo/ : PDF de présentation ; balisage et équivalence accessible complète non établis.|
|13.4|NA|Pas de version accessible du PDF identifiée avant correction.|
|13.5|NC|Emojis décoratifs lus dans les titres, domaines, messages et commandes.|
|13.6|C|Symboles signifiants accompagnés de texte (distance, internat, téléphone).|
|13.7|C|Pas de clignotement programmé ni animation de flash dans les interfaces.|
|13.8|C|Vidéos sur commande, pause disponible ; pas de carrousel automatique.|
|13.9|C|Aucun verrouillage portrait/paysage dans les pages.|
|13.10|C|Carte : boutons +/−, clavier et vue Liste pour les gestes de déplacement/zoom.|
|13.11|C|Actions via click, activation au relâchement ; déplacement de carte réversible.|
|13.12|NA|Pas de commande par mouvement de l’appareil.|

Sources : [critères RGAA](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/), [modèle de déclaration](https://accessibilite.numerique.gouv.fr/obligations/declaration-accessibilite/). FAQ conservée sans modification selon la consigne.
