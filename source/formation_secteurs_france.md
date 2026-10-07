# Ajouts France — formations et entreprises

Contrôle du 2026-10-07 ; référence Git `a92cb50e0656d7f2133cca89b101d0171086b3b2`.

250 intitulés CAP/bac pro dans 30 académies ; 84 absents de la table : 51 CAP (dont 5 CAPa), 33 bacs pro. Ils représentent 1304 occurrences formation–établissement dans ces fichiers (pas des places ni des offres d'emploi).

Les 168 entrées historiques et leurs associations sont conservées. 36 secteurs et 65 codes NAF sont ajoutés ; aucune ancienne liste NAF n'est modifiée.

## Méthode et portée

Comparaison après normalisation CAP agricole/CAPa, casse, accents, ligatures, tirets et apostrophes. Choix des secteurs à partir des objectifs, débouchés et exemples de métiers Onisep. Correspondance RNCP relue par intitulé et code diplôme dans le catalogue de certifications LBA ; aucun rapprochement incertain imposé. Réponses de recherche LBA nationales par RNCP et niveau, agrégées par NAF, offres séparées des recruteurs potentiels ; simple indice non exhaustif, jamais une preuve de stage disponible.

Sources : fiches Onisep déjà téléchargées pour la mission Après le lycée (dates et SHA-256 dans le JSON), catalogue de certifications et recherche LBA consultés le 7 octobre 2026, [NAF rév. 2 de l’Insee](https://www.insee.fr/fr/information/2120875). La NAF 2025 n’est pas utilisée pour cette collecte en NAF rév. 2.

Les nombres LBA ci-dessous sont des résultats de recherche, pas des recrutements réalisés. Les offres et les recruteurs potentiels sont séparés. La réponse est partielle (souvent 150 recruteurs) et les codes ROME peuvent englober plusieurs options. On ne somme pas les lignes entre diplômes. Les offres déléguées à des CFA et celles explicitement inactives sont exclues des agrégats ; le filtre de niveau accepte aussi les niveaux non renseignés. Le filtre de nom du nouveau secteur des fleurs n’est pas appliqué au signal NAF : celui-ci peut donc être plus large.

Aucune coordonnée de candidat, de contact ou d’entreprise n’est enregistrée dans ce dossier. La clé API est lue uniquement en mémoire. Aucun téléchargement Sirene n’est lancé par les scripts d’audit.

Cette PR prépare les sources. Les JSON et pages actuellement servis restent inchangés. Régénérer le catalogue de stages avec ces sources ajoutera ces formations et secteurs : la future mission nationale devra conserver le catalogue Île-de-France publié.

## Points à relire en priorité

- RNCP non rapproché : CAP agent de développement des activités locales option tourisme (Guyane), et certificat polynésien petite et moyenne hôtellerie. Ce dernier est rattaché par Onisep à Mana, en Guyane.
- Trois bacs pro de conduite des entreprises maritimes : code ROME N3202 fluvial renvoyé par la certification ; les secteurs maritimes retenus suivent Onisep. Aucun lien fluvial déduit de ce seul code.
- Réparation/accordage des instruments : le code 95.29Z reste dans le secteur historique de pressing. Couverture partielle assumée ; aucune entreprise déplacée et aucun lien trompeur ajouté au pressing.
- NAF larges : équitation, élevage, animaleries de laboratoire, armurerie, tourisme, photonique, parcs et déchets dangereux. Vérifier la spécialité réelle avant de proposer un stage.
- Artisans individuels toujours exclus de la future collecte : limite forte pour la maréchalerie et les métiers d’art. Le filtre nouveau 32.99Z sur les noms de fabricants de fleurs demande une relecture.

## Nouveaux codes NAF

| Code | Libellé Insee | Secteur |
|---|---|---|
| [01.12Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.12Z) | Culture du riz | Cultures spécialisées, vergers, cultures tropicales |
| [01.14Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.14Z) | Culture de la canne à sucre | Cultures spécialisées, vergers, cultures tropicales |
| [01.21Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.21Z) | Culture de la vigne | Viticulture, vinification |
| [01.22Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.22Z) | Culture de fruits tropicaux et subtropicaux | Cultures spécialisées, vergers, cultures tropicales |
| [01.23Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.23Z) | Culture d'agrumes | Cultures spécialisées, vergers, cultures tropicales |
| [01.24Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.24Z) | Culture de fruits à pépins et à noyau | Cultures spécialisées, vergers, cultures tropicales |
| [01.25Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.25Z) | Culture d'autres fruits d'arbres ou d'arbustes et de fruits à coque | Cultures spécialisées, vergers, cultures tropicales |
| [01.26Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.26Z) | Culture de fruits oléagineux | Cultures spécialisées, vergers, cultures tropicales |
| [01.27Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.27Z) | Culture de plantes à boissons | Cultures spécialisées, vergers, cultures tropicales |
| [01.28Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.28Z) | Culture de plantes à épices, aromatiques, médicinales et pharmaceutiques | Cultures spécialisées, vergers, cultures tropicales |
| [01.29Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.29Z) | Autres cultures permanentes | Cultures spécialisées, vergers, cultures tropicales |
| [01.41Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.41Z) | Élevage de vaches laitières | Élevage bovin, ovin, caprin, porcin, volailles |
| [01.42Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.42Z) | Élevage d'autres bovins et de buffles | Élevage bovin, ovin, caprin, porcin, volailles |
| [01.43Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.43Z) | Élevage de chevaux et d'autres équidés | Élevage de chevaux, haras |
| [01.45Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.45Z) | Élevage d'ovins et de caprins | Élevage bovin, ovin, caprin, porcin, volailles |
| [01.46Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.46Z) | Élevage de porcins | Élevage bovin, ovin, caprin, porcin, volailles |
| [01.47Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.47Z) | Élevage de volailles | Élevage bovin, ovin, caprin, porcin, volailles |
| [01.49Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.49Z) | Élevage d'autres animaux | Autres élevages (dont animaux de compagnie, apiculture) |
| [01.61Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.61Z) | Activités de soutien aux cultures | Travaux agricoles, services aux cultures |
| [01.62Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/01.62Z) | Activités de soutien à la production animale | Services à l'élevage, maréchalerie |
| [02.10Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/02.10Z) | Sylviculture et autres activités forestières | Forêts, travaux forestiers |
| [02.20Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/02.20Z) | Exploitation forestière | Forêts, travaux forestiers |
| [02.40Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/02.40Z) | Services de soutien à l'exploitation forestière | Forêts, travaux forestiers |
| [03.11Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/03.11Z) | Pêche en mer | Pêche professionnelle |
| [03.12Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/03.12Z) | Pêche en eau douce | Pêche professionnelle |
| [03.21Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/03.21Z) | Aquaculture en mer | Aquaculture, pisciculture, conchyliculture |
| [03.22Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/03.22Z) | Aquaculture en eau douce | Aquaculture, pisciculture, conchyliculture |
| [10.11Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/10.11Z) | Transformation et conservation de la viande de boucherie | Transformation de viandes |
| [10.12Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/10.12Z) | Transformation et conservation de la viande de volaille | Transformation de viandes |
| [10.20Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/10.20Z) | Transformation et conservation de poisson, de crustacés et de mollusques | Transformation de poissons, crustacés, mollusques |
| [11.02A](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/11.02A) | Fabrication de vins effervescents | Viticulture, vinification |
| [11.02B](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/11.02B) | Vinification | Viticulture, vinification |
| [16.10A](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/16.10A) | Sciage et rabotage du bois, hors imprégnation | Scieries, préparation du bois |
| [16.10B](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/16.10B) | Imprégnation du bois | Scieries, préparation du bois |
| [16.29Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/16.29Z) | Fabrication d'objets divers en bois ; fabrication d'objets en liège, vannerie et sparterie | Objets en bois, liège, vannerie |
| [23.61Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/23.61Z) | Fabrication d'éléments en béton pour la construction | Éléments préfabriqués en béton |
| [24.51Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/24.51Z) | Fonderie de fonte | Fonderies |
| [24.52Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/24.52Z) | Fonderie d'acier | Fonderies |
| [24.53Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/24.53Z) | Fonderie de métaux légers | Fonderies |
| [24.54Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/24.54Z) | Fonderie d'autres métaux non ferreux | Fonderies |
| [25.40Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/25.40Z) | Fabrication d'armes et de munitions | Armurerie, fabrication d’armes |
| [26.51B](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/26.51B) | Fabrication d'instrumentation scientifique et technique | Optique, photonique, instruments de mesure |
| [26.70Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/26.70Z) | Fabrication de matériels optique et photographique | Optique, photonique, instruments de mesure |
| [30.11Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/30.11Z) | Construction de navires et de structures flottantes | Construction de navires |
| [32.11Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/32.11Z) | Frappe de monnaie | Fabrication de monnaies, médailles |
| [32.99Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/32.99Z) | Autres activités manufacturières n.c.a. | Fleurs artificielles, parures de mode |
| [38.22Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/38.22Z) | Traitement et élimination des déchets dangereux | Traitement des déchets dangereux |
| [46.31Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/46.31Z) | Commerce de gros (commerce interentreprises) de fruits et légumes | Grossistes en fruits et légumes |
| [46.32A](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/46.32A) | Commerce de gros (commerce interentreprises) de viandes de boucherie | Grossistes en viandes |
| [46.32B](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/46.32B) | Commerce de gros (commerce interentreprises) de produits à base de viande | Grossistes en viandes |
| [46.38A](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/46.38A) | Commerce de gros (commerce interentreprises) de poissons, crustacés et mollusques | Grossistes en poissons, crustacés, mollusques |
| [49.39C](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/49.39C) | Téléphériques et remontées mécaniques | Remontées mécaniques, téléphériques |
| [49.42Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/49.42Z) | Services de déménagement | Déménagement |
| [50.10Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/50.10Z) | Transports maritimes et côtiers de passagers | Navigation maritime, plaisance professionnelle |
| [50.20Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/50.20Z) | Transports maritimes et côtiers de fret | Navigation maritime, plaisance professionnelle |
| [50.30Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/50.30Z) | Transports fluviaux de passagers | Navigation fluviale |
| [50.40Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/50.40Z) | Transports fluviaux de fret | Navigation fluviale |
| [53.10Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/53.10Z) | Activités de poste dans le cadre d'une obligation de service universel | Poste, courrier |
| [72.11Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/72.11Z) | Recherche-développement en biotechnologie | Laboratoires de recherche scientifique |
| [72.19Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/72.19Z) | Recherche-développement en autres sciences physiques et naturelles | Laboratoires de recherche scientifique |
| [79.90Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/79.90Z) | Autres services de réservation et activités connexes | Guides, offices de tourisme |
| [85.51Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/85.51Z) | Enseignement de disciplines sportives et d'activités de loisirs | Écoles de sport, équitation |
| [85.52Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/85.52Z) | Enseignement culturel | Enseignement culturel, conservatoires |
| [91.04Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/91.04Z) | Gestion des jardins botaniques et zoologiques et des réserves naturelles | Parcs naturels, jardins botaniques et zoologiques |
| [93.19Z](https://www.insee.fr/fr/metadonnees/nafr2/sousClasse/93.19Z) | Autres activités liées au sport | Activités sportives (dont écuries de course) |

## Justifications par formation

### 1. bac pro agroéquipement — ajout France

**Types d’entreprises :** Horticulture, maraîchage, agriculture ; Travaux agricoles, services aux cultures ; Matériels agricoles, engins de chantier ; Forêts, travaux forestiers ; Mairies, administrations.

**Lecture Onisep :** Conduite et entretien des matériels en exploitation, CUMA, travaux agricoles et forestiers ; distribution de matériels et collectivités citées.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7685).
[RNCP38384](https://www.francecompetences.fr/recherche/rncp/38384/) ; CFD `40321001` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38384). ROME : A1101 — Conduite d''engins agricoles et forestiers.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38384&target_diploma_level=4) : 22 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Horticulture, maraîchage, agriculture : 1 / 38.
- Travaux agricoles, services aux cultures : 0 / 3.
- Matériels agricoles, engins de chantier : 0 / 0.
- Forêts, travaux forestiers : 0 / 0.
- Mairies, administrations : 0 / 0.

### 2. bac pro boucher charcutier traiteur — ajout France

**Types d’entreprises :** Boucherie, charcuterie, poissonnerie ; Traiteurs ; Supermarchés, grandes surfaces ; Industrie agroalimentaire ; Transformation de viandes ; Grossistes en viandes.

**Lecture Onisep :** Préparation et vente de viandes en artisanat, grande distribution, industrie et commerce de gros.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.4245).
[RNCP37602](https://www.francecompetences.fr/recherche/rncp/37602/) ; CFD `40022104` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37602). ROME : D1101 — Boucherie ; D1106 — Vente en alimentation ; D1103 — Charcuterie - traiteur.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37602&target_diploma_level=4) : 335 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Boucherie, charcuterie, poissonnerie : 32 / 10.
- Traiteurs : 3 / 0.
- Supermarchés, grandes surfaces : 16 / 111.
- Industrie agroalimentaire : 2 / 0.
- Transformation de viandes : 4 / 12.
- Grossistes en viandes : 0 / 3.

### 3. bac pro conduite d'activités d'élevage et d'hébergement dans le secteur canin-félin — ajout France

**Types d’entreprises :** Autres élevages (dont animaux de compagnie, apiculture) ; Vétérinaires, soins aux animaux.

**Lecture Onisep :** Élevages canins et félins ; pensions et hébergement d'animaux.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.9957).
[RNCP39155](https://www.francecompetences.fr/recherche/rncp/39155/) ; CFD `40321214` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39155). ROME : A1408 — Élevage d''animaux sauvages ou de compagnie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39155&target_diploma_level=4) : 4 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Autres élevages (dont animaux de compagnie, apiculture) : 0 / 2.
- Vétérinaires, soins aux animaux : 2 / 0.

**Limites / cas incertains :**
- 01.49Z mêle animaux de compagnie, apiculture et autres élevages ; vérifier la spécialité de chaque établissement.
- Le secteur historique contient 96.09Z, qui couvre aussi des services sans rapport avec les animaux ; aucune catégorie existante n'est modifiée ici.

### 4. bac pro conduite de productions aquacoles — ajout France

**Types d’entreprises :** Aquaculture, pisciculture, conchyliculture.

**Lecture Onisep :** Élevage de poissons, coquillages et algues, en eau douce et en mer.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7409).
[RNCP36787](https://www.francecompetences.fr/recherche/rncp/36787/) ; CFD `40321213` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP36787). ROME : A1404 — Aquaculture.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP36787&target_diploma_level=4) : 5 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Aquaculture, pisciculture, conchyliculture : 0 / 86.

### 5. bac pro conduite et gestion de l'entreprise agricole — ajout France

**Types d’entreprises :** Horticulture, maraîchage, agriculture ; Cultures spécialisées, vergers, cultures tropicales ; Élevage bovin, ovin, caprin, porcin, volailles ; Autres élevages (dont animaux de compagnie, apiculture).

**Lecture Onisep :** Exploitations de cultures et d'élevages ; apiculture citée parmi les métiers.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7690).
[RNCP38316](https://www.francecompetences.fr/recherche/rncp/38316/) ; CFD `40321004` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38316). ROME : A1409 — Élevage de lapins et volailles ; A1416 — Polyculture, élevage ; A1407 — Élevage bovin ou équin ; A1410 — Élevage ovin ou caprin ; A1411 — Élevage porcin.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38316&target_diploma_level=4) : 23 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Horticulture, maraîchage, agriculture : 4 / 56.
- Cultures spécialisées, vergers, cultures tropicales : 0 / 0.
- Élevage bovin, ovin, caprin, porcin, volailles : 9 / 83.
- Autres élevages (dont animaux de compagnie, apiculture) : 0 / 0.

**Limites / cas incertains :**
- 01.49Z mêle animaux de compagnie, apiculture et autres élevages ; vérifier la spécialité de chaque établissement.

### 6. bac pro conduite et gestion de l'entreprise hippique — ajout France

**Types d’entreprises :** Élevage de chevaux, haras ; Clubs et salles de sport ; Activités sportives (dont écuries de course) ; Écoles de sport, équitation.

**Lecture Onisep :** Écuries de course, établissements équestres et écuries de propriétaires.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7692).
[RNCP38076](https://www.francecompetences.fr/recherche/rncp/38076/) ; CFD `40321211` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38076). ROME : A1407 — Élevage bovin ou équin.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38076&target_diploma_level=4) : 6 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Élevage de chevaux, haras : 0 / 0.
- Clubs et salles de sport : 0 / 0.
- Activités sportives (dont écuries de course) : 0 / 0.
- Écoles de sport, équitation : 0 / 0.

**Limites / cas incertains :**
- Le secteur historique regroupe plusieurs sports ; seuls les établissements équestres conviennent à cette formation.
- 93.19Z comprend les écuries de course mais aussi d'autres sports ; le code ne suffit pas à identifier une écurie.
- 85.51Z comprend les écoles d'équitation et celles d'autres sports ; spécialité à vérifier.

### 7. bac pro conduite et gestion de l'entreprise vitivinicole — ajout France

**Types d’entreprises :** Viticulture, vinification ; Laboratoires d'analyses et d'essais.

**Lecture Onisep :** Exploitations viticoles, coopératives de vinification et laboratoires d'œnologie cités.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7694).
[RNCP38077](https://www.francecompetences.fr/recherche/rncp/38077/) ; CFD `40321113` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38077). ROME : A1413 — Fermentation de boissons alcoolisées ; A1405 — Arboriculture et viticulture.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38077&target_diploma_level=4) : 30 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Viticulture, vinification : 2 / 49.
- Laboratoires d'analyses et d'essais : 0 / 0.

### 8. bac pro conduite et gestion des entreprises maritimes - commerce/plaisance professionnelle option voile — ajout France

**Types d’entreprises :** Navigation maritime, plaisance professionnelle.

**Lecture Onisep :** Navigation commerciale à voile, transport maritime et plaisance avec équipage.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6058).
[RNCP40092](https://www.francecompetences.fr/recherche/rncp/40092/) ; CFD `40031112` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40092). ROME : N3202 — Exploitation du transport fluvial.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40092&target_diploma_level=4) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Navigation maritime, plaisance professionnelle : 0 / 0.

**Limites / cas incertains :**
- Discordance RNCP/API : N3202 (Exploitation du transport fluvial) pour un diplôme maritime. Le signal LBA associé ne justifie pas un lien vers le fluvial ; choix fondé sur la fiche Onisep.

### 9. bac pro conduite et gestion des entreprises maritimes - commerce/plaisance professionnelle option yacht — ajout France

**Types d’entreprises :** Navigation maritime, plaisance professionnelle.

**Lecture Onisep :** Navigation commerciale sur yacht et plaisance professionnelle avec équipage.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6105).
[RNCP40092](https://www.francecompetences.fr/recherche/rncp/40092/) ; CFD `40031113` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40092). ROME : N3202 — Exploitation du transport fluvial.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40092&target_diploma_level=4) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Navigation maritime, plaisance professionnelle : 0 / 0.

**Limites / cas incertains :**
- Discordance RNCP/API : N3202 (Exploitation du transport fluvial) pour un diplôme maritime. Le signal LBA associé ne justifie pas un lien vers le fluvial ; choix fondé sur la fiche Onisep.

### 10. bac pro conduite et gestion des entreprises maritimes - pêche — ajout France

**Types d’entreprises :** Pêche professionnelle ; Navigation maritime, plaisance professionnelle.

**Lecture Onisep :** Conduite de navires de pêche ; navigation commerciale également citée dans les débouchés.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2912).
[RNCP40091](https://www.francecompetences.fr/recherche/rncp/40091/) ; CFD `40021304` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40091). ROME : N3202 — Exploitation du transport fluvial.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40091&target_diploma_level=4) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Pêche professionnelle : 0 / 0.
- Navigation maritime, plaisance professionnelle : 0 / 0.

**Limites / cas incertains :**
- Discordance RNCP/API : N3202 (Exploitation du transport fluvial) pour un diplôme maritime. Le signal LBA associé ne justifie pas un lien vers le fluvial ; choix fondé sur la fiche Onisep.

### 11. bac pro cultures marines — ajout France

**Types d’entreprises :** Aquaculture, pisciculture, conchyliculture ; Grossistes en poissons, crustacés, mollusques.

**Lecture Onisep :** Aquaculture marine et commercialisation des produits marins.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1083).
[RNCP40097](https://www.francecompetences.fr/recherche/rncp/40097/) ; CFD `40021204` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40097). ROME : A1404 — Aquaculture.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40097&target_diploma_level=4) : 5 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Aquaculture, pisciculture, conchyliculture : 0 / 86.
- Grossistes en poissons, crustacés, mollusques : 0 / 44.

### 12. bac pro fonderie — ajout France

**Types d’entreprises :** Fonderies ; Laboratoires d'analyses et d'essais.

**Lecture Onisep :** Production de pièces moulées et contrôle en laboratoire de fonderie.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.10903).
[RNCP40082](https://www.francecompetences.fr/recherche/rncp/40082/) ; CFD `40022310` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40082). ROME : H2907 — Conduite d''installation de production des métaux.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40082&target_diploma_level=4) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Fonderies : 0 / 40.
- Laboratoires d'analyses et d'essais : 0 / 0.

**Limites / cas incertains :**
- Le secteur comprend différents métaux ; pour les CAP bronze/cuivre, vérifier la spécialité de la fonderie.

### 13. bac pro forêt — ajout France

**Types d’entreprises :** Forêts, travaux forestiers.

**Lecture Onisep :** Travaux sylvicoles et exploitation forestière, y compris coopératives et ONF.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7418).
[RNCP36790](https://www.francecompetences.fr/recherche/rncp/36790/) ; CFD `40321303` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP36790). ROME : A1205 — Sylviculture ; A1201 — Bûcheronnage et élagage.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP36790&target_diploma_level=4) : 8 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Forêts, travaux forestiers : 1 / 3.

### 14. bac pro gestion des milieux naturels et de la faune — ajout France

**Types d’entreprises :** Parcs naturels, jardins botaniques et zoologiques ; Forêts, travaux forestiers ; Paysagistes, espaces verts ; Mairies, administrations ; Associations (animation, solidarité).

**Lecture Onisep :** Entretien et protection des espaces naturels ; collectivités, entreprises et associations.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7419).
[RNCP36789](https://www.francecompetences.fr/recherche/rncp/36789/) ; CFD `40321302` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP36789). ROME : A1204 — Protection du patrimoine naturel ; A1202 — Entretien des espaces naturels.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP36789&target_diploma_level=4) : 6 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Parcs naturels, jardins botaniques et zoologiques : 0 / 4.
- Forêts, travaux forestiers : 0 / 0.
- Paysagistes, espaces verts : 0 / 9.
- Mairies, administrations : 0 / 0.
- Associations (animation, solidarité) : 0 / 0.

**Limites / cas incertains :**
- 91.04Z regroupe des structures différentes ; vérifier le service d'accueil pour la formation choisie.

### 15. bac pro interventions sur le patrimoine bâti option B charpente — ajout France

**Types d’entreprises :** Construction, maçonnerie, gros œuvre ; Menuiserie, agencement, serrurerie.

**Lecture Onisep :** Charpente et restauration du bâti ancien ; entreprises qualifiées en patrimoine.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6086).
[RNCP41014](https://www.francecompetences.fr/recherche/rncp/41014/) ; CFD `40023206` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP41014). ROME : H2206 — Réalisation de menuiserie bois et tonnellerie ; F1501 — Montage de structures et de charpentes bois ; F1610 — Pose et restauration de couvertures ; F1703 — Maçonnerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP41014&target_diploma_level=4) : 137 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Construction, maçonnerie, gros œuvre : 41 / 62.
- Menuiserie, agencement, serrurerie : 7 / 69.

### 16. bac pro maintenance environnementale et propreté des espaces urbains — ajout France

**Types d’entreprises :** Nettoyage, propreté ; Déchets, recyclage, assainissement ; Mairies, administrations.

**Lecture Onisep :** Assainissement, collecte, recyclage, salubrité et services des collectivités.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.11088).
[RNCP40311](https://www.francecompetences.fr/recherche/rncp/40311/) ; CFD `40034307` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40311). ROME : K2301 — Distribution et assainissement d''eau ; K2303 — Nettoyage des espaces urbains ; K2304 — Revalorisation de produits industriels ; K2305 — Salubrité et traitement de nuisibles.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40311&target_diploma_level=4) : 15 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Nettoyage, propreté : 1 / 14.
- Déchets, recyclage, assainissement : 1 / 49.
- Mairies, administrations : 0 / 0.

### 17. bac pro métiers de l'entretien des textiles option A blanchisserie — ajout France

**Types d’entreprises :** Pressing, blanchisserie, retouches ; Hôpitaux, cliniques, laboratoires ; Personnes âgées (EHPAD, résidences) ; Hôtels ; Restaurants.

**Lecture Onisep :** Blanchisseries et services intégrés dans les établissements de santé, d'hébergement et de restauration.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6852).
[RNCP42128](https://www.francecompetences.fr/recherche/rncp/42128/) ; CFD `40024005` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42128). ROME : D1205 — Nettoyage d''articles textiles ou cuirs ; K2201 — Blanchisserie industrielle.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42128&target_diploma_level=4) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Pressing, blanchisserie, retouches : 0 / 129.
- Hôpitaux, cliniques, laboratoires : 0 / 0.
- Personnes âgées (EHPAD, résidences) : 0 / 0.
- Hôtels : 0 / 0.
- Restaurants : 0 / 0.

### 18. bac pro métiers de l'entretien des textiles option B pressing — ajout France

**Types d’entreprises :** Pressing, blanchisserie, retouches.

**Lecture Onisep :** Entretien des vêtements en pressing.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6853).
[RNCP42128](https://www.francecompetences.fr/recherche/rncp/42128/) ; CFD `40024006` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42128). ROME : D1205 — Nettoyage d''articles textiles ou cuirs ; K2201 — Blanchisserie industrielle.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42128&target_diploma_level=4) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Pressing, blanchisserie, retouches : 0 / 129.

### 19. bac pro métiers du cuir option chaussures — ajout France

**Types d’entreprises :** Cuir, maroquinerie, cordonnerie.

**Lecture Onisep :** Fabrication et prototypage de chaussures, du luxe aux petites séries.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6057).
[RNCP37230](https://www.francecompetences.fr/recherche/rncp/37230/) ; CFD `40024301` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37230). ROME : H2401 — Assemblage - montage d''articles en cuirs, peaux ; H2407 — Conduite de machine de transformation et de finition des cuirs et peaux ; H2409 — Coupe cuir, textile et matériaux souples ; H2411 — Montage de prototype cuir et matériaux souples ; H2415 — Contrôle en industrie du cuir et du textile.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37230&target_diploma_level=4) : 27 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Cuir, maroquinerie, cordonnerie : 13 / 48.

### 20. bac pro métiers du cuir option sellerie garnissage — ajout France

**Types d’entreprises :** Cuir, maroquinerie, cordonnerie ; Garages, carrosseries (voitures) ; Bateaux, nautisme ; Aéronautique.

**Lecture Onisep :** La rubrique Objectifs de la formation cite explicitement la réalisation de prototypes en sellerie automobile, aéronautique et navale. Ajout des garages/carrosseries, du nautisme et de l'aéronautique pour les ateliers de garnissage et d'aménagement intérieur.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6088).
[RNCP37230](https://www.francecompetences.fr/recherche/rncp/37230/) ; CFD `40024303` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37230). ROME : H2401 — Assemblage - montage d''articles en cuirs, peaux ; H2407 — Conduite de machine de transformation et de finition des cuirs et peaux ; H2409 — Coupe cuir, textile et matériaux souples ; H2411 — Montage de prototype cuir et matériaux souples ; H2415 — Contrôle en industrie du cuir et du textile.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37230&target_diploma_level=4) : 27 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Cuir, maroquinerie, cordonnerie : 13 / 48.
- Garages, carrosseries (voitures) : 0 / 0.
- Bateaux, nautisme : 0 / 0.
- Aéronautique : 0 / 0.

**Limites / cas incertains :**
- Ces secteurs sont larges : retenir les établissements disposant d'une activité de sellerie, de garnissage ou d'aménagement intérieur, et non tous les garages ou toutes les entreprises aéronautiques et nautiques. Aucun signal LBA positif n'est observé pour ces catégories dans la réponse conservée ; les objectifs Onisep étayent ces associations.

### 21. bac pro métiers et arts de la pierre — ajout France

**Types d’entreprises :** Construction, maçonnerie, gros œuvre.

**Lecture Onisep :** Taille de pierre, construction et restauration du patrimoine ; 23.70Z déjà présent.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.586).
[RNCP38223](https://www.francecompetences.fr/recherche/rncp/38223/) ; CFD `40023208` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38223). ROME : F1612 — Taille et décoration de pierres.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38223&target_diploma_level=4) : 10 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Construction, maçonnerie, gros œuvre : 2 / 0.

### 22. bac pro optique photonique : technologies de la lumière — ajout France

**Types d’entreprises :** Optique, photonique, instruments de mesure ; Maintenance d'équipements, ascenseurs ; Laboratoires d'analyses et d'essais ; Laboratoires de recherche scientifique.

**Lecture Onisep :** Fabrication, assemblage, essais et maintenance de systèmes optiques ; recherche-développement citée.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.8760).
[RNCP37490](https://www.francecompetences.fr/recherche/rncp/37490/) ; CFD `40025518` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37490). ROME : H1209 — Intervention technique en études et développement électronique ; I1305 — Installation et maintenance électronique.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37490&target_diploma_level=4) : 15 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Optique, photonique, instruments de mesure : 0 / 8.
- Maintenance d'équipements, ascenseurs : 0 / 21.
- Laboratoires d'analyses et d'essais : 0 / 16.
- Laboratoires de recherche scientifique : 0 / 0.

**Limites / cas incertains :**
- 26.51B couvre aussi une instrumentation sans photonique ; vérifier l'activité précise.
- 72.11Z et 72.19Z ne garantissent ni une animalerie ni un service optique : vérifier le domaine du laboratoire.

### 23. bac pro plastiques et composites — ajout France

**Types d’entreprises :** Plastique, verre, matériaux.

**Lecture Onisep :** Entreprises productrices et transformatrices de plastiques et composites.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.533).
[RNCP38566](https://www.francecompetences.fr/recherche/rncp/38566/) ; CFD `40022503` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38566). ROME : H2504 — Encadrement d''équipe en industrie de transformation.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38566&target_diploma_level=4) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Plastique, verre, matériaux : 0 / 46.

### 24. bac pro poissonnier écailler traiteur — ajout France

**Types d’entreprises :** Boucherie, charcuterie, poissonnerie ; Supermarchés, grandes surfaces ; Traiteurs ; Restaurants ; Transformation de poissons, crustacés, mollusques.

**Lecture Onisep :** Poissonnerie artisanale, rayons spécialisés, transformation et restauration.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.3532).
[RNCP37927](https://www.francecompetences.fr/recherche/rncp/37927/) ; CFD `40031209` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37927). ROME : D1105 — Poissonnerie ; D1103 — Charcuterie - traiteur.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37927&target_diploma_level=4) : 48 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Boucherie, charcuterie, poissonnerie : 16 / 13.
- Supermarchés, grandes surfaces : 1 / 104.
- Traiteurs : 3 / 0.
- Restaurants : 0 / 0.
- Transformation de poissons, crustacés, mollusques : 0 / 0.

### 25. bac pro polyvalent navigant pont/machine — ajout France

**Types d’entreprises :** Navigation maritime, plaisance professionnelle ; Pêche professionnelle ; Bateaux, nautisme ; Construction de navires.

**Lecture Onisep :** Travail au pont et aux machines ; armements et réparation navale.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1008).
[RNCP40090](https://www.francecompetences.fr/recherche/rncp/40090/) ; CFD `40025011` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40090). ROME : N3102 — Equipage de la navigation maritime ; A1415 — Equipage de la pêche ; I1605 — Mécanique de marine.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40090&target_diploma_level=4) : 3 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Navigation maritime, plaisance professionnelle : 0 / 15.
- Pêche professionnelle : 0 / 35.
- Bateaux, nautisme : 1 / 0.
- Construction de navires : 0 / 0.

### 26. bac pro services aux personnes et animation dans les territoires — ajout France

**Types d’entreprises :** Aide à domicile ; Crèches, petite enfance ; Hôpitaux, cliniques, laboratoires ; Personnes âgées (EHPAD, résidences) ; Loisirs, animation ; Mairies, administrations ; Associations (animation, solidarité).

**Lecture Onisep :** Services aux personnes et animation territoriale, à domicile ou en structures collectives.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7629).
[RNCP36788](https://www.francecompetences.fr/recherche/rncp/36788/) ; CFD `40333002` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP36788). ROME : M1601 — Accueil et renseignements ; K1302 — Assistance auprès d''adultes ; K1303 — Assistance auprès d''enfants ; G1202 — Animation d''activités culturelles ou ludiques ; K1305 — Intervention sociale et familiale.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP36788&target_diploma_level=4) : 308 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Aide à domicile : 54 / 0.
- Crèches, petite enfance : 7 / 6.
- Hôpitaux, cliniques, laboratoires : 0 / 0.
- Personnes âgées (EHPAD, résidences) : 0 / 101.
- Loisirs, animation : 19 / 2.
- Mairies, administrations : 0 / 21.
- Associations (animation, solidarité) : 3 / 7.

### 27. bac pro technicien conseil vente en animalerie — ajout France

**Types d’entreprises :** Fleuristes, jardineries ; Supermarchés, grandes surfaces ; Magasins spécialisés (bricolage, maison, sport, high-tech…).

**Lecture Onisep :** Animaleries, jardineries et rayons animaliers des grandes surfaces.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7706).
[RNCP38856](https://www.francecompetences.fr/recherche/rncp/38856/) ; CFD `40321203` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38856). ROME : D1210 — Vente en animalerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38856&target_diploma_level=4) : 10 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Fleuristes, jardineries : 0 / 144.
- Supermarchés, grandes surfaces : 0 / 0.
- Magasins spécialisés (bricolage, maison, sport, high-tech…) : 0 / 0.

**Limites / cas incertains :**
- Regroupement historique très large : seuls les magasins disposant du rayon ou de l'atelier concerné conviennent.

### 28. bac pro technicien de scierie — ajout France

**Types d’entreprises :** Scieries, préparation du bois.

**Lecture Onisep :** Première transformation du bois en scierie.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1037).
[RNCP37307](https://www.francecompetences.fr/recherche/rncp/37307/) ; CFD `40023406` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37307). ROME : H2205 — Première transformation de bois d''oeuvre.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37307&target_diploma_level=4) : 8 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Scieries, préparation du bois : 2 / 12.

### 29. bac pro technicien en expérimentation animale — ajout France

**Types d’entreprises :** Laboratoires de recherche scientifique ; Chimie, pharmacie, cosmétiques, papier ; Hôpitaux, cliniques, laboratoires ; Vétérinaires, soins aux animaux ; Parcs naturels, jardins botaniques et zoologiques.

**Lecture Onisep :** Animaleries de recherche, laboratoires pharmaceutiques, hôpitaux, cliniques vétérinaires et parcs animaliers.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7708).
[RNCP38385](https://www.francecompetences.fr/recherche/rncp/38385/) ; CFD `40321212` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38385). ROME : A1501 — Aide aux soins animaux.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38385&target_diploma_level=4) : 8 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Laboratoires de recherche scientifique : 0 / 0.
- Chimie, pharmacie, cosmétiques, papier : 0 / 0.
- Hôpitaux, cliniques, laboratoires : 0 / 0.
- Vétérinaires, soins aux animaux : 2 / 7.
- Parcs naturels, jardins botaniques et zoologiques : 0 / 0.

**Limites / cas incertains :**
- 72.11Z et 72.19Z ne garantissent ni une animalerie ni un service optique : vérifier le domaine du laboratoire.
- Le secteur historique contient 96.09Z, qui couvre aussi des services sans rapport avec les animaux ; aucune catégorie existante n'est modifiée ici.
- 91.04Z regroupe des structures différentes ; vérifier le service d'accueil pour la formation choisie.

### 30. bac pro techniques d'interventions sur installations nucléaires — ajout France

**Types d’entreprises :** Production et distribution d'énergie ; Déchets, recyclage, assainissement ; Traitement des déchets dangereux ; Maintenance d'équipements, ascenseurs.

**Lecture Onisep :** Interventions en production nucléaire, maintenance, décontamination et traitement des déchets.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1155).
[RNCP38573](https://www.francecompetences.fr/recherche/rncp/38573/) ; CFD `40034305` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38573). ROME : I1503 — Intervention en milieux et produits nocifs.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38573&target_diploma_level=4) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Production et distribution d'énergie : 0 / 0.
- Déchets, recyclage, assainissement : 0 / 47.
- Traitement des déchets dangereux : 0 / 21.
- Maintenance d'équipements, ascenseurs : 0 / 0.

**Limites / cas incertains :**
- 38.22Z n'est pas réservé au nucléaire. L'accès à certains travaux et sites doit être organisé avec le lycée.

### 31. bac pro transport fluvial — ajout France

**Types d’entreprises :** Navigation fluviale.

**Lecture Onisep :** Navigation fluviale de fret et de passagers.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.9256).
[RNCP38570](https://www.francecompetences.fr/recherche/rncp/38570/) ; CFD `40031115` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38570). ROME : N3103 — Navigation fluviale.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38570&target_diploma_level=4) : 0 offres retournées (0 exclues), 47 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Navigation fluviale : 0 / 13.

### 32. bac pro transports par câbles et remontées mécaniques — ajout France

**Types d’entreprises :** Remontées mécaniques, téléphériques ; Transport de voyageurs ; Maintenance d'équipements, ascenseurs.

**Lecture Onisep :** Exploitation et maintenance des remontées mécaniques, transports urbains et entreprises de montage.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.8260).
[RNCP37309](https://www.francecompetences.fr/recherche/rncp/37309/) ; CFD `40025109` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37309). ROME : N4402 — Exploitation et manoeuvre des remontées mécaniques.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37309&target_diploma_level=4) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Remontées mécaniques, téléphériques : 0 / 11.
- Transport de voyageurs : 0 / 128.
- Maintenance d'équipements, ascenseurs : 0 / 0.

### 33. bac pro électromécanicien marine — ajout France

**Types d’entreprises :** Navigation maritime, plaisance professionnelle ; Pêche professionnelle ; Bateaux, nautisme ; Construction de navires.

**Lecture Onisep :** Entretien des machines à bord et dans les chantiers navals ou services techniques d'armements.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.3035).
[RNCP40093](https://www.francecompetences.fr/recherche/rncp/40093/) ; CFD `40025010` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40093). ROME : I1605 — Mécanique de marine.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40093&target_diploma_level=4) : 3 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Navigation maritime, plaisance professionnelle : 0 / 8.
- Pêche professionnelle : 0 / 10.
- Bateaux, nautisme : 1 / 69.
- Construction de navires : 0 / 9.

### 34. CAP accordeur de pianos — ajout France

**Types d’entreprises :** Céramique, verre d'art, instruments de musique ; Magasins spécialisés (bricolage, maison, sport, high-tech…) ; Enseignement culturel, conservatoires.

**Lecture Onisep :** Fabricants, magasins de musique, conservatoires et écoles employant des accordeurs.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.512).
[RNCP36339](https://www.francecompetences.fr/recherche/rncp/36339/) ; CFD `50032308` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP36339). ROME : B1501 — Fabrication et réparation d''instruments de musique.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP36339&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Céramique, verre d'art, instruments de musique : 0 / 1.
- Magasins spécialisés (bricolage, maison, sport, high-tech…) : 0 / 0.
- Enseignement culturel, conservatoires : 0 / 0.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.
- Regroupement historique très large : seuls les magasins disposant du rayon ou de l'atelier concerné conviennent.
- Les réparateurs/accordeurs classés en 95.29Z restent dans le secteur historique Pressing, blanchisserie, retouches. Ce secteur n'est pas associé au diplôme car son libellé serait trompeur ; couverture partielle à résoudre dans une évolution distincte sans déplacer les entreprises existantes.

### 35. CAP agent de développement des activités locales option tourisme (Guyane) — ajout France

**Types d’entreprises :** Guides, offices de tourisme ; Loisirs, animation.

**Lecture Onisep :** Accueil et accompagnement touristique sur circuits amazoniens.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.3834).

RNCP, ROME et signal LBA : **non rapprochés**, sans estimation.

**Limites / cas incertains :**
- 79.90Z couvre aussi d'autres services de réservation. Le diplôme concerne le tourisme amazonien.
- Aucun rapprochement RNCP sûr dans le catalogue LBA consulté : codes ROME et signal par RNCP laissés absents, sans substitution par un diplôme voisin.

### 36. CAP agent de prévention et de médiation — ajout France

**Types d’entreprises :** Mairies, administrations ; Associations (animation, solidarité) ; Agences immobilières, gestion de logements ; Transport de voyageurs.

**Lecture Onisep :** Médiation sociale dans les quartiers, logements et transports.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.369).
[RNCP37240](https://www.francecompetences.fr/recherche/rncp/37240/) ; CFD `50034002` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37240). ROME : K1204 — Médiation sociale et facilitation de la vie en société ; K1205 — Information sociale.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37240&target_diploma_level=3) : 21 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Mairies, administrations : 0 / 0.
- Associations (animation, solidarité) : 0 / 0.
- Agences immobilières, gestion de logements : 0 / 0.
- Transport de voyageurs : 0 / 5.

### 37. CAP agent vérificateur d'appareils extincteurs — ajout France

**Types d’entreprises :** Maintenance d'équipements, ascenseurs.

**Lecture Onisep :** Installation, entretien et vérification des extincteurs par les entreprises de maintenance.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.289).
[RNCP38228](https://www.francecompetences.fr/recherche/rncp/38228/) ; CFD `50025133` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38228). ROME : I1203 — Maintenance des bâtiments et des locaux.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38228&target_diploma_level=3) : 39 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Maintenance d'équipements, ascenseurs : 0 / 0.

### 38. CAPa agricultures des régions chaudes — ajout France

**Types d’entreprises :** Horticulture, maraîchage, agriculture ; Cultures spécialisées, vergers, cultures tropicales ; Élevage bovin, ovin, caprin, porcin, volailles ; Autres élevages (dont animaux de compagnie, apiculture) ; Aquaculture, pisciculture, conchyliculture.

**Lecture Onisep :** Exploitations tropicales : productions végétales et animales, dont aquaculture.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2907).
[RNCP38854](https://www.francecompetences.fr/recherche/rncp/38854/) ; CFD `50321010` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38854). ROME : A1414 — Horticulture et maraîchage ; A1416 — Polyculture, élevage ; A1404 — Aquaculture.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38854&target_diploma_level=3) : 38 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Horticulture, maraîchage, agriculture : 17 / 0.
- Cultures spécialisées, vergers, cultures tropicales : 2 / 0.
- Élevage bovin, ovin, caprin, porcin, volailles : 0 / 0.
- Autres élevages (dont animaux de compagnie, apiculture) : 0 / 0.
- Aquaculture, pisciculture, conchyliculture : 0 / 86.

**Limites / cas incertains :**
- 01.49Z mêle animaux de compagnie, apiculture et autres élevages ; vérifier la spécialité de chaque établissement.

### 39. CAPa lad-cavalier d'entraînement — ajout France

**Types d’entreprises :** Activités sportives (dont écuries de course) ; Élevage de chevaux, haras ; Clubs et salles de sport.

**Lecture Onisep :** Écuries d'entraînement, hippodromes et entreprises des courses hippiques.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2906).
[RNCP38387](https://www.francecompetences.fr/recherche/rncp/38387/) ; CFD `50321235` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38387). ROME : L1401 — Sportif professionnel.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38387&target_diploma_level=3) : 4 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Activités sportives (dont écuries de course) : 0 / 12.
- Élevage de chevaux, haras : 0 / 0.
- Clubs et salles de sport : 0 / 138.

**Limites / cas incertains :**
- 93.19Z comprend les écuries de course mais aussi d'autres sports ; le code ne suffit pas à identifier une écurie.
- Le secteur historique regroupe plusieurs sports ; seuls les établissements équestres conviennent à cette formation.

### 40. CAPa maréchal-ferrant — ajout France

**Types d’entreprises :** Services à l'élevage, maréchalerie ; Élevage de chevaux, haras ; Activités sportives (dont écuries de course).

**Lecture Onisep :** Entreprises de maréchalerie et écuries employant un maréchal-ferrant.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.879).
[RNCP38388](https://www.francecompetences.fr/recherche/rncp/38388/) ; CFD `50321236` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38388). ROME : A1502 — Podologie animale.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38388&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Services à l'élevage, maréchalerie : 0 / 41.
- Élevage de chevaux, haras : 0 / 0.
- Activités sportives (dont écuries de course) : 0 / 0.

**Limites / cas incertains :**
- 01.62Z inclut la maréchalerie mais aussi d'autres services d'élevage. Les entrepreneurs individuels resteront exclus, ce qui réduit fortement la couverture de ce métier.
- 93.19Z comprend les écuries de course mais aussi d'autres sports ; le code ne suffit pas à identifier une écurie.

### 41. CAPa palefrenier soigneur — ajout France

**Types d’entreprises :** Élevage de chevaux, haras ; Activités sportives (dont écuries de course) ; Clubs et salles de sport ; Écoles de sport, équitation.

**Lecture Onisep :** Haras, centres d'entraînement, établissements de tourisme équestre et poneys-clubs.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1467).
[RNCP38389](https://www.francecompetences.fr/recherche/rncp/38389/) ; CFD `50321237` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38389). ROME : A1403 — Aide d''élevage agricole et aquacole.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38389&target_diploma_level=3) : 16 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Élevage de chevaux, haras : 6 / 7.
- Activités sportives (dont écuries de course) : 0 / 0.
- Clubs et salles de sport : 1 / 0.
- Écoles de sport, équitation : 0 / 0.

**Limites / cas incertains :**
- 93.19Z comprend les écuries de course mais aussi d'autres sports ; le code ne suffit pas à identifier une écurie.
- Le secteur historique regroupe plusieurs sports ; seuls les établissements équestres conviennent à cette formation.
- 85.51Z comprend les écoles d'équitation et celles d'autres sports ; spécialité à vérifier.

### 42. CAPa travaux forestiers — ajout France

**Types d’entreprises :** Forêts, travaux forestiers.

**Lecture Onisep :** Entreprises de travaux forestiers, exploitants, coopératives et ONF.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.4573).
[RNCP38391](https://www.francecompetences.fr/recherche/rncp/38391/) ; CFD `50321314` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38391). ROME : A1205 — Sylviculture ; A1201 — Bûcheronnage et élagage.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38391&target_diploma_level=3) : 11 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Forêts, travaux forestiers : 3 / 3.

### 43. CAP armurerie (fabrication et réparation) — ajout France

**Types d’entreprises :** Armurerie, fabrication d’armes ; Magasins spécialisés (bricolage, maison, sport, high-tech…).

**Lecture Onisep :** Fabricants d'armes et armureries commerciales dotées d'un atelier.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.480).
[RNCP38394](https://www.francecompetences.fr/recherche/rncp/38394/) ; CFD `50025136` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38394). ROME : H2901 — Ajustement et montage de fabrication.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38394&target_diploma_level=3) : 18 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Armurerie, fabrication d’armes : 0 / 0.
- Magasins spécialisés (bricolage, maison, sport, high-tech…) : 0 / 0.

**Limites / cas incertains :**
- 25.40Z regroupe armurerie sportive et production militaire. L'Onisep décrit ici les armes de chasse et de tir ; vérification de l'activité et des conditions de stage indispensable.
- Regroupement historique très large : seuls les magasins disposant du rayon ou de l'atelier concerné conviennent.

### 44. CAP arts du bois option marqueteur — ajout France

**Types d’entreprises :** Ébénisterie, meubles, restauration de meubles ; Objets en bois, liège, vannerie.

**Lecture Onisep :** Ateliers d'ébénisterie et restauration de mobilier ; marqueterie d'objets d'art.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5388).
[RNCP37301](https://www.francecompetences.fr/recherche/rncp/37301/) ; CFD `50023432` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37301). ROME : H2207 — Réalisation de meubles en bois ; H2206 — Réalisation de menuiserie bois et tonnellerie ; B1302 — Décoration d''objets d''art et artisanaux ; F1503 — Réalisation - installation d''ossatures bois ; H2208 — Réalisation d''ouvrages décoratifs en bois.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37301&target_diploma_level=3) : 51 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Ébénisterie, meubles, restauration de meubles : 3 / 50.
- Objets en bois, liège, vannerie : 0 / 5.

### 45. CAP arts du bois option sculpteur ornemaniste — ajout France

**Types d’entreprises :** Ébénisterie, meubles, restauration de meubles ; Objets en bois, liège, vannerie.

**Lecture Onisep :** Sculpture sur bois, décoration et restauration du mobilier.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5387).
[RNCP37301](https://www.francecompetences.fr/recherche/rncp/37301/) ; CFD `50023430` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37301). ROME : H2207 — Réalisation de meubles en bois ; H2206 — Réalisation de menuiserie bois et tonnellerie ; B1302 — Décoration d''objets d''art et artisanaux ; F1503 — Réalisation - installation d''ossatures bois ; H2208 — Réalisation d''ouvrages décoratifs en bois.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37301&target_diploma_level=3) : 51 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Ébénisterie, meubles, restauration de meubles : 3 / 50.
- Objets en bois, liège, vannerie : 0 / 5.

### 46. CAP arts du bois option tourneur — ajout France

**Types d’entreprises :** Objets en bois, liège, vannerie ; Ébénisterie, meubles, restauration de meubles ; Céramique, verre d'art, instruments de musique.

**Lecture Onisep :** Tournage d'objets en bois, éléments de meubles et instruments de musique.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5355).
[RNCP37301](https://www.francecompetences.fr/recherche/rncp/37301/) ; CFD `50023431` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37301). ROME : H2207 — Réalisation de meubles en bois ; H2206 — Réalisation de menuiserie bois et tonnellerie ; B1302 — Décoration d''objets d''art et artisanaux ; F1503 — Réalisation - installation d''ossatures bois ; H2208 — Réalisation d''ouvrages décoratifs en bois.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37301&target_diploma_level=3) : 51 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Objets en bois, liège, vannerie : 0 / 5.
- Ébénisterie, meubles, restauration de meubles : 3 / 50.
- Céramique, verre d'art, instruments de musique : 0 / 22.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.

### 47. CAP arts du verre et du cristal — ajout France

**Types d’entreprises :** Céramique, verre d'art, instruments de musique ; Plastique, verre, matériaux.

**Lecture Onisep :** Verreries et cristalleries artisanales ; décoration du verre.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1983).
[RNCP36426](https://www.francecompetences.fr/recherche/rncp/36426/) ; CFD `50022428` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP36426). ROME : B1602 — Réalisation d''objets artistiques et fonctionnels en verre.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP36426&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Céramique, verre d'art, instruments de musique : 0 / 49.
- Plastique, verre, matériaux : 0 / 92.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.

### 48. CAP assistant luthier du quatuor — ajout France

**Types d’entreprises :** Céramique, verre d'art, instruments de musique ; Magasins spécialisés (bricolage, maison, sport, high-tech…).

**Lecture Onisep :** Ateliers de lutherie du quatuor et magasins de musique ; les conservatoires sont ici des clients.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.7155).
[RNCP42108](https://www.francecompetences.fr/recherche/rncp/42108/) ; CFD `50023450` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42108). ROME : B1501 — Fabrication et réparation d''instruments de musique.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42108&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Céramique, verre d'art, instruments de musique : 0 / 1.
- Magasins spécialisés (bricolage, maison, sport, high-tech…) : 0 / 0.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.
- Regroupement historique très large : seuls les magasins disposant du rayon ou de l'atelier concerné conviennent.
- Les réparateurs/accordeurs classés en 95.29Z restent dans le secteur historique Pressing, blanchisserie, retouches. Ce secteur n'est pas associé au diplôme car son libellé serait trompeur ; couverture partielle à résoudre dans une évolution distincte sans déplacer les entreprises existantes.

### 49. CAP aéronautique option structure — ajout France

**Types d’entreprises :** Aéronautique.

**Lecture Onisep :** Construction et maintenance des structures d'aéronefs.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.6112).
[RNCP37700](https://www.francecompetences.fr/recherche/rncp/37700/) ; CFD `50025307` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37700). ROME : I1602 — Maintenance d''aéronefs ; H2602 — Câblage électrique et électromécanique ; H1506 — Intervention technique qualité en mécanique et travail des métaux ; H2901 — Ajustement et montage de fabrication ; H2909 — Montage-assemblage mécanique.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37700&target_diploma_level=3) : 33 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Aéronautique : 0 / 12.

### 50. CAP boucher — ajout France

**Types d’entreprises :** Boucherie, charcuterie, poissonnerie ; Supermarchés, grandes surfaces ; Transformation de viandes ; Grossistes en viandes ; Restauration collective (cantines, entreprises).

**Lecture Onisep :** Boucheries, rayons de supermarchés, transformation de viande, grossistes et cuisines centrales.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.8785).
[RNCP37535](https://www.francecompetences.fr/recherche/rncp/37535/) ; CFD `50022143` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37535). ROME : D1101 — Boucherie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37535&target_diploma_level=3) : 217 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Boucherie, charcuterie, poissonnerie : 71 / 10.
- Supermarchés, grandes surfaces : 51 / 111.
- Transformation de viandes : 9 / 12.
- Grossistes en viandes : 0 / 3.
- Restauration collective (cantines, entreprises) : 0 / 0.

### 51. CAP bronzier option B ciseleur en bronze — ajout France

**Types d’entreprises :** Chaudronnerie, soudure, structures métalliques ; Ébénisterie, meubles, restauration de meubles ; Électronique, matériel électrique ; Fonderies.

**Lecture Onisep :** Ciselure de bronzes d'ameublement, de luminaires et de sculptures en lien avec les fondeurs d'art.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5371).
[RNCP42134](https://www.francecompetences.fr/recherche/rncp/42134/) ; CFD `50022350` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42134). ROME : B1601 — Métallerie d''art.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42134&target_diploma_level=3) : 1 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Chaudronnerie, soudure, structures métalliques : 1 / 45.
- Ébénisterie, meubles, restauration de meubles : 0 / 0.
- Électronique, matériel électrique : 0 / 1.
- Fonderies : 0 / 1.

**Limites / cas incertains :**
- Le secteur comprend différents métaux ; pour les CAP bronze/cuivre, vérifier la spécialité de la fonderie.

### 52. CAP cannage paillage en ameublement — ajout France

**Types d’entreprises :** Ébénisterie, meubles, restauration de meubles ; Objets en bois, liège, vannerie.

**Lecture Onisep :** Cannage et paillage de sièges dans les ateliers de mobilier.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.687).
[RNCP39649](https://www.francecompetences.fr/recherche/rncp/39649/) ; CFD `50023420` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39649). ROME : B1401 — Réalisation d''objets en lianes, fibres et brins végétaux.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39649&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Ébénisterie, meubles, restauration de meubles : 0 / 119.
- Objets en bois, liège, vannerie : 0 / 0.

### 53. CAP certificat polynésien d'aptitude professionnelle option petite et moyenne hôtellerie — ajout France

**Types d’entreprises :** Hôtels ; Restaurants.

**Lecture Onisep :** Accueil, entretien, cuisine et service dans la petite et moyenne hôtellerie polynésienne.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.3218).

RNCP, ROME et signal LBA : **non rapprochés**, sans estimation.

**Limites / cas incertains :**
- Aucun rapprochement RNCP sûr dans le catalogue LBA consulté : codes ROME et signal par RNCP laissés absents, sans substitution par un diplôme voisin.
- Anomalie Onisep à confirmer : ce diplôme polynésien est proposé dans les données nationales au lycée Léopold Elfort, à Mana (Guyane). Son intitulé est conservé sans réinterprétation.

### 54. CAP charcuterie-traiteur — ajout France

**Types d’entreprises :** Boucherie, charcuterie, poissonnerie ; Traiteurs ; Supermarchés, grandes surfaces ; Industrie agroalimentaire ; Hôtels ; Restaurants ; Restauration collective (cantines, entreprises).

**Lecture Onisep :** Charcuterie artisanale ou industrielle, rayons spécialisés et restauration.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.9681).
[RNCP38631](https://www.francecompetences.fr/recherche/rncp/38631/) ; CFD `50022144` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38631). ROME : D1103 — Charcuterie - traiteur.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38631&target_diploma_level=3) : 49 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Boucherie, charcuterie, poissonnerie : 18 / 13.
- Traiteurs : 3 / 0.
- Supermarchés, grandes surfaces : 3 / 104.
- Industrie agroalimentaire : 2 / 14.
- Hôtels : 0 / 0.
- Restaurants : 0 / 0.
- Restauration collective (cantines, entreprises) : 0 / 0.

### 55. CAP charpentier de marine — ajout France

**Types d’entreprises :** Bateaux, nautisme ; Construction de navires.

**Lecture Onisep :** Construction, entretien et restauration de bateaux en bois.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2520).
[RNCP38409](https://www.francecompetences.fr/recherche/rncp/38409/) ; CFD `50023444` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38409). ROME : F1503 — Réalisation - installation d''ossatures bois.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38409&target_diploma_level=3) : 16 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Bateaux, nautisme : 0 / 0.
- Construction de navires : 0 / 0.

### 56. CAP composites, plastiques chaudronnés — ajout France

**Types d’entreprises :** Plastique, verre, matériaux ; Bateaux, nautisme ; Aéronautique.

**Lecture Onisep :** Fabrication de pièces plastiques et composites ; construction navale et aéronautique citées.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1496).
[RNCP38432](https://www.francecompetences.fr/recherche/rncp/38432/) ; CFD `50022510` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38432). ROME : H3201 — Conduite d''équipement de formage des plastiques et caoutchoucs ; H2902 — Chaudronnerie - tôlerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38432&target_diploma_level=3) : 15 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Plastique, verre, matériaux : 0 / 0.
- Bateaux, nautisme : 0 / 0.
- Aéronautique : 2 / 0.

### 57. CAP conducteur-opérateur de scierie — ajout France

**Types d’entreprises :** Scieries, préparation du bois.

**Lecture Onisep :** Conduite des installations de première transformation du bois.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2135).
[RNCP37304](https://www.francecompetences.fr/recherche/rncp/37304/) ; CFD `50023443` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37304). ROME : H2202 — Conduite d''équipement de fabrication de l''ameublement et du bois.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37304&target_diploma_level=3) : 7 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Scieries, préparation du bois : 0 / 6.

### 58. CAP constructeur d'ouvrages en béton armé — ajout France

**Types d’entreprises :** Construction, maçonnerie, gros œuvre ; Travaux publics, routes, réseaux ; Éléments préfabriqués en béton.

**Lecture Onisep :** Construction et préfabrication d'ouvrages en béton armé.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.10971).
[RNCP40335](https://www.francecompetences.fr/recherche/rncp/40335/) ; CFD `50023225` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40335). ROME : F1701 — Construction en béton.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40335&target_diploma_level=3) : 46 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Construction, maçonnerie, gros œuvre : 12 / 90.
- Travaux publics, routes, réseaux : 0 / 50.
- Éléments préfabriqués en béton : 0 / 4.

### 59. CAP cordonnier bottier — ajout France

**Types d’entreprises :** Cuir, maroquinerie, cordonnerie.

**Lecture Onisep :** Fabrication artisanale ou de luxe et réparation de chaussures.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.505).
[RNCP37366](https://www.francecompetences.fr/recherche/rncp/37366/) ; CFD `50024313` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37366). ROME : B1802 — Réalisation d''articles en cuir et matériaux souples (hors vêtement).

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37366&target_diploma_level=3) : 25 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Cuir, maroquinerie, cordonnerie : 22 / 74.

### 60. CAP déménageur sur véhicule utilitaire léger — ajout France

**Types d’entreprises :** Déménagement.

**Lecture Onisep :** Entreprises de déménagement de particuliers et d'entreprises.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2661).
[RNCP37895](https://www.francecompetences.fr/recherche/rncp/37895/) ; CFD `50031119` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37895). ROME : N1102 — Déménagement.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37895&target_diploma_level=3) : 1 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Déménagement : 0 / 70.

### 61. CAP facture d'instruments à vent — ajout France

**Types d’entreprises :** Céramique, verre d'art, instruments de musique ; Magasins spécialisés (bricolage, maison, sport, high-tech…) ; Enseignement culturel, conservatoires ; Spectacle, musées, bibliothèques.

**Lecture Onisep :** Fabrication, réparation et maintenance d'instruments à vent ; magasins, conservatoires et lieux culturels.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.12769).
[RNCP42420](https://www.francecompetences.fr/recherche/rncp/42420/) ; CFD `50032318` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42420). ROME : B1501 — Fabrication et réparation d''instruments de musique.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42420&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Céramique, verre d'art, instruments de musique : 0 / 1.
- Magasins spécialisés (bricolage, maison, sport, high-tech…) : 0 / 0.
- Enseignement culturel, conservatoires : 0 / 0.
- Spectacle, musées, bibliothèques : 0 / 0.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.
- Regroupement historique très large : seuls les magasins disposant du rayon ou de l'atelier concerné conviennent.
- Les réparateurs/accordeurs classés en 95.29Z restent dans le secteur historique Pressing, blanchisserie, retouches. Ce secteur n'est pas associé au diplôme car son libellé serait trompeur ; couverture partielle à résoudre dans une évolution distincte sans déplacer les entreprises existantes.

### 62. CAP fleuriste de mode — ajout France

**Types d’entreprises :** Couture, confection ; Spectacle, musées, bibliothèques ; Fleurs artificielles, parures de mode.

**Lecture Onisep :** Ateliers indépendants ou intégrés à la haute couture et au spectacle vivant.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.9917).
[RNCP39035](https://www.francecompetences.fr/recherche/rncp/39035/) ; CFD `50024132` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39035). ROME : B1804 — Réalisation d''ouvrages d''art en fils.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39035&target_diploma_level=3) : 6 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Couture, confection : 0 / 25.
- Spectacle, musées, bibliothèques : 0 / 101.
- Fleurs artificielles, parures de mode : 0 / 0.

**Limites / cas incertains :**
- 32.99Z est très large : filtre sur nom/enseigne FLEUR, FLORAL, PLUMASS ou PARUR. Ce filtre peut manquer des ateliers ou produire des faux positifs ; aucune entreprise vérifiée dans cette PR.

### 63. CAP glacier fabricant — ajout France

**Types d’entreprises :** Chocolaterie, confiserie, glaces ; Boulangerie, pâtisserie ; Traiteurs ; Restaurants.

**Lecture Onisep :** Fabrication artisanale ou industrielle de glaces ; pâtissiers, traiteurs et restaurants.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.669).
[RNCP41941](https://www.francecompetences.fr/recherche/rncp/41941/) ; CFD `50022138` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP41941). ROME : D1104 — Pâtisserie, confiserie, chocolaterie et glacerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP41941&target_diploma_level=3) : 235 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Chocolaterie, confiserie, glaces : 2 / 6.
- Boulangerie, pâtisserie : 147 / 44.
- Traiteurs : 0 / 0.
- Restaurants : 5 / 0.

### 64. CAP lutherie guitare — ajout France

**Types d’entreprises :** Céramique, verre d'art, instruments de musique ; Magasins spécialisés (bricolage, maison, sport, high-tech…) ; Enseignement culturel, conservatoires ; Spectacle, musées, bibliothèques.

**Lecture Onisep :** Ateliers de guitares, manufactures, magasins, conservatoires et musées.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.12772).
[RNCP42422](https://www.francecompetences.fr/recherche/rncp/42422/) ; CFD `50032317` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42422). ROME : B1501 — Fabrication et réparation d''instruments de musique.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42422&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Céramique, verre d'art, instruments de musique : 0 / 1.
- Magasins spécialisés (bricolage, maison, sport, high-tech…) : 0 / 0.
- Enseignement culturel, conservatoires : 0 / 0.
- Spectacle, musées, bibliothèques : 0 / 0.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.
- Regroupement historique très large : seuls les magasins disposant du rayon ou de l'atelier concerné conviennent.
- Les réparateurs/accordeurs classés en 95.29Z restent dans le secteur historique Pressing, blanchisserie, retouches. Ce secteur n'est pas associé au diplôme car son libellé serait trompeur ; couverture partielle à résoudre dans une évolution distincte sans déplacer les entreprises existantes.

### 65. CAP maintenance nautique — ajout France

**Types d’entreprises :** Bateaux, nautisme.

**Lecture Onisep :** Réparation et entretien de bateaux de plaisance.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.8856).
[RNCP37670](https://www.francecompetences.fr/recherche/rncp/37670/) ; CFD `50025217` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37670). ROME : I1310 — Maintenance mécanique industrielle ; I1605 — Mécanique de marine ; I1604 — Mécanique automobile et entretien de véhicules ; I1607 — Réparation de cycles, motocycles et motoculteurs de loisirs.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37670&target_diploma_level=3) : 173 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Bateaux, nautisme : 0 / 0.

### 66. CAP maritime — ajout France

**Types d’entreprises :** Pêche professionnelle ; Navigation maritime, plaisance professionnelle.

**Lecture Onisep :** Équipages de pêche, commerce, ferries et vedettes à passagers.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1398).
[RNCP39406](https://www.francecompetences.fr/recherche/rncp/39406/) ; CFD `50021308` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39406). ROME : N3102 — Equipage de la navigation maritime ; I1605 — Mécanique de marine.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39406&target_diploma_level=3) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Pêche professionnelle : 0 / 10.
- Navigation maritime, plaisance professionnelle : 0 / 8.

### 67. CAP maritime conchyliculture — ajout France

**Types d’entreprises :** Aquaculture, pisciculture, conchyliculture.

**Lecture Onisep :** Entreprises d'élevage et de production de coquillages.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1399).
[RNCP40230](https://www.francecompetences.fr/recherche/rncp/40230/) ; CFD `50021203` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP40230). ROME : A1404 — Aquaculture.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP40230&target_diploma_level=3) : 6 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Aquaculture, pisciculture, conchyliculture : 0 / 86.

### 68. CAP menuisier en sièges — ajout France

**Types d’entreprises :** Ébénisterie, meubles, restauration de meubles.

**Lecture Onisep :** Fabrication de sièges, prototypes et restauration de meubles anciens.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.639).
[RNCP39648](https://www.francecompetences.fr/recherche/rncp/39648/) ; CFD `50023411` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39648). ROME : H2206 — Réalisation de menuiserie bois et tonnellerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39648&target_diploma_level=3) : 30 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Ébénisterie, meubles, restauration de meubles : 1 / 0.

### 69. CAP mouleur noyauteur : cuivre et bronze — ajout France

**Types d’entreprises :** Fonderies.

**Lecture Onisep :** Moulage et noyautage du cuivre et du bronze.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.671).
[RNCP42114](https://www.francecompetences.fr/recherche/rncp/42114/) ; CFD `50022324` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42114). ROME : H2908 — Modelage de matériaux non métalliques ; H2910 — Moulage sable.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42114&target_diploma_level=3) : 1 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Fonderies : 0 / 5.

**Limites / cas incertains :**
- Le secteur comprend différents métaux ; pour les CAP bronze/cuivre, vérifier la spécialité de la fonderie.

### 70. CAP métiers de la gravure option C gravure en modelé — ajout France

**Types d’entreprises :** Fabrication de monnaies, médailles ; Bijouterie, horlogerie ; Usinage, mécanique, outillage.

**Lecture Onisep :** Gravure de matrices, moules, monnaies, médailles et pièces d'orfèvrerie.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5653).
[RNCP39808](https://www.francecompetences.fr/recherche/rncp/39808/) ; CFD `50032222` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39808). ROME : B1303 — Gravure - ciselure.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39808&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Fabrication de monnaies, médailles : 0 / 0.
- Bijouterie, horlogerie : 0 / 24.
- Usinage, mécanique, outillage : 0 / 0.

### 71. CAP métiers du plâtre et de l'isolation — ajout France

**Types d’entreprises :** Peinture, plâtre, carrelage, sols, isolation.

**Lecture Onisep :** Entreprises de plâtrerie et d'isolation intérieure.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.912).
[RNCP39032](https://www.francecompetences.fr/recherche/rncp/39032/) ; CFD `50023326` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39032). ROME : F1604 — Montage d''agencements ; F1703 — Maçonnerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39032&target_diploma_level=3) : 122 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Peinture, plâtre, carrelage, sols, isolation : 6 / 34.

### 72. CAP opérateur/opératrice de service - relation client et livraison — ajout France

**Types d’entreprises :** Poste, courrier ; Transport de marchandises, livraison ; Secrétariat, accueil, centres d'appels.

**Lecture Onisep :** Distribution de courrier et colis, tournées de livraison et relation clientèle.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1253).
[RNCP38403](https://www.francecompetences.fr/recherche/rncp/38403/) ; CFD `50031123` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38403). ROME : M1603 — Distribution de documents ; N4105 — Conduite et livraison par tournées sur courte distance.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38403&target_diploma_level=3) : 107 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Poste, courrier : 2 / 125.
- Transport de marchandises, livraison : 1 / 0.
- Secrétariat, accueil, centres d'appels : 0 / 0.

### 73. CAP plumasserie — ajout France

**Types d’entreprises :** Couture, confection ; Spectacle, musées, bibliothèques ; Fleurs artificielles, parures de mode.

**Lecture Onisep :** Ateliers de plumasserie indépendants ou intégrés à la haute couture et au spectacle ; le type Fleurs artificielles, parures de mode repère aussi les plumassiers par son filtre PLUMASS.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.9921).
[RNCP39134](https://www.francecompetences.fr/recherche/rncp/39134/) ; CFD `50024133` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39134). ROME : B1801 — Réalisation d''articles de chapellerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39134&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Couture, confection : 0 / 6.
- Spectacle, musées, bibliothèques : 0 / 0.
- Fleurs artificielles, parures de mode : 0 / 0.

**Limites / cas incertains :**
- Le code 32.99Z et le filtre sur les noms ne couvrent pas tous les ateliers de plumasserie et peuvent produire des faux positifs. Le signal LBA par NAF est plus large que ce filtre. Aucun code de production brute de plumes n'est ajouté.

### 74. CAP poissonnier écailler — ajout France

**Types d’entreprises :** Boucherie, charcuterie, poissonnerie ; Grossistes en poissons, crustacés, mollusques ; Transformation de poissons, crustacés, mollusques ; Supermarchés, grandes surfaces ; Restaurants ; Traiteurs.

**Lecture Onisep :** Poissonneries, mareyeurs, transformation, rayons spécialisés et restauration.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1393).
[RNCP42137](https://www.francecompetences.fr/recherche/rncp/42137/) ; CFD `50031221` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42137). ROME : D1105 — Poissonnerie.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42137&target_diploma_level=3) : 19 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Boucherie, charcuterie, poissonnerie : 3 / 0.
- Grossistes en poissons, crustacés, mollusques : 2 / 0.
- Transformation de poissons, crustacés, mollusques : 0 / 2.
- Supermarchés, grandes surfaces : 0 / 126.
- Restaurants : 0 / 0.
- Traiteurs : 0 / 0.

### 75. CAP primeur — ajout France

**Types d’entreprises :** Primeur, fromagerie, épicerie fine, cave ; Supermarchés, grandes surfaces ; Grossistes en fruits et légumes ; Entrepôts, logistique.

**Lecture Onisep :** Commerce de fruits et légumes, grossistes, coopératives et entrepôts.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2725).
[RNCP37604](https://www.francecompetences.fr/recherche/rncp/37604/) ; CFD `50031222` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37604). ROME : D1106 — Vente en alimentation ; D1107 — Vente en gros de produits frais.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37604&target_diploma_level=3) : 298 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Primeur, fromagerie, épicerie fine, cave : 8 / 6.
- Supermarchés, grandes surfaces : 9 / 96.
- Grossistes en fruits et légumes : 0 / 0.
- Entrepôts, logistique : 2 / 0.

### 76. CAP rentrayeur option B tapisseries — ajout France

**Types d’entreprises :** Tapisserie, décoration textile ; Spectacle, musées, bibliothèques.

**Lecture Onisep :** Restauration et entretien de tapisseries, ateliers artisanaux et manufactures.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5390).
[RNCP42133](https://www.francecompetences.fr/recherche/rncp/42133/) ; CFD `50024126` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP42133). ROME : B1804 — Réalisation d''ouvrages d''art en fils.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP42133&target_diploma_level=3) : 6 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Tapisserie, décoration textile : 0 / 12.
- Spectacle, musées, bibliothèques : 0 / 101.

**Limites / cas incertains :**
- La réparation de tapisseries n'est pas isolée par la NAF ; 13.92Z (déjà présent) couvre les tapisseries tissées à la main. 13.93Z n'est pas ajouté : il concerne surtout tapis et moquettes.

### 77. CAP sellerie générale — ajout France

**Types d’entreprises :** Cuir, maroquinerie, cordonnerie ; Tapisserie, décoration textile ; Ébénisterie, meubles, restauration de meubles.

**Lecture Onisep :** Sellerie-garnissage et confection d'équipements souples, de sièges, de tentes et de stores.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1499).
[RNCP39037](https://www.francecompetences.fr/recherche/rncp/39037/) ; CFD `50024318` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39037). ROME : B1802 — Réalisation d''articles en cuir et matériaux souples (hors vêtement).

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39037&target_diploma_level=3) : 25 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Cuir, maroquinerie, cordonnerie : 22 / 74.
- Tapisserie, décoration textile : 0 / 0.
- Ébénisterie, meubles, restauration de meubles : 0 / 0.

### 78. CAP sellier harnacheur — ajout France

**Types d’entreprises :** Cuir, maroquinerie, cordonnerie ; Élevage de chevaux, haras ; Clubs et salles de sport ; Activités sportives (dont écuries de course) ; Écoles de sport, équitation.

**Lecture Onisep :** Fabrication, réparation et adaptation de selles, harnais et équipements équins. La fiche diplôme cite les ateliers de sellerie ; les centres équestres, haras et écuries sont ajoutés à la suite de la relecture comme pistes complémentaires, sous réserve d'une activité réelle de sellerie.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.503).
[RNCP37905](https://www.francecompetences.fr/recherche/rncp/37905/) ; CFD `50024321` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37905). ROME : B1802 — Réalisation d''articles en cuir et matériaux souples (hors vêtement).

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37905&target_diploma_level=3) : 25 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Cuir, maroquinerie, cordonnerie : 22 / 74.
- Élevage de chevaux, haras : 0 / 0.
- Clubs et salles de sport : 0 / 0.
- Activités sportives (dont écuries de course) : 0 / 0.
- Écoles de sport, équitation : 0 / 0.

**Limites / cas incertains :**
- Un centre équestre ou une écurie peut être client du sellier sans l'employer. Ces liens ne conviennent à une PFMP que si la structure dispose d'un atelier ou d'un professionnel de sellerie pouvant encadrer les activités du diplôme ; à vérifier avec le lycée.
- Les codes des clubs, écoles de sport et activités sportives couvrent aussi d'autres sports. Vérifier qu'il s'agit bien d'équitation et d'une activité de sellerie ; aucun signal LBA positif n'est observé pour ces catégories dans la réponse conservée.

### 79. CAP souffleur de verre option enseigne lumineuse — ajout France

**Types d’entreprises :** Enseignes, signalétique, marquage ; Plastique, verre, matériaux ; Céramique, verre d'art, instruments de musique ; Électronique, matériel électrique.

**Lecture Onisep :** Soufflage de tubes de verre pour enseignes et fabrication spécialisée de verrerie.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.5823).
[RNCP39940](https://www.francecompetences.fr/recherche/rncp/39940/) ; CFD `50022429` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP39940). ROME : B1602 — Réalisation d''objets artistiques et fonctionnels en verre.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP39940&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Enseignes, signalétique, marquage : 0 / 0.
- Plastique, verre, matériaux : 0 / 92.
- Céramique, verre d'art, instruments de musique : 0 / 49.
- Électronique, matériel électrique : 0 / 0.

**Limites / cas incertains :**
- Regroupement historique large : sélectionner l'atelier adapté (verre ou instruments) ; aucun secteur ancien renommé.

### 80. CAP tapissier-tapissière d'ameublement en décor — ajout France

**Types d’entreprises :** Tapisserie, décoration textile ; Ébénisterie, meubles, restauration de meubles.

**Lecture Onisep :** Confection de décors textiles et tapisserie d'ameublement, fabrication et commerce.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.2501).
[RNCP37247](https://www.francecompetences.fr/recherche/rncp/37247/) ; CFD `50024239` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37247). ROME : B1806 — Tapisserie - décoration en ameublement.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37247&target_diploma_level=3) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Tapisserie, décoration textile : 0 / 21.
- Ébénisterie, meubles, restauration de meubles : 2 / 39.

### 81. CAP tapissier-tapissière d'ameublement en siège — ajout France

**Types d’entreprises :** Ébénisterie, meubles, restauration de meubles ; Tapisserie, décoration textile.

**Lecture Onisep :** Garnissage et restauration de sièges ; commerce de tissus et de mobilier.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.502).
[RNCP37248](https://www.francecompetences.fr/recherche/rncp/37248/) ; CFD `50024238` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37248). ROME : B1806 — Tapisserie - décoration en ameublement.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37248&target_diploma_level=3) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Ébénisterie, meubles, restauration de meubles : 2 / 39.
- Tapisserie, décoration textile : 0 / 21.

### 82. CAP transport fluvial — ajout France

**Types d’entreprises :** Navigation fluviale.

**Lecture Onisep :** Transport de marchandises ou de passagers sur les voies fluviales.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.9255).
[RNCP38571](https://www.francecompetences.fr/recherche/rncp/38571/) ; CFD `50031125` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP38571). ROME : N3103 — Navigation fluviale.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP38571&target_diploma_level=3) : 0 offres retournées (0 exclues), 47 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Navigation fluviale : 0 / 13.

### 83. CAP transports par câbles et remontées mécaniques — ajout France

**Types d’entreprises :** Remontées mécaniques, téléphériques ; Maintenance d'équipements, ascenseurs.

**Lecture Onisep :** Exploitation, montage et maintenance des installations de transport par câbles.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.8606).
[RNCP37306](https://www.francecompetences.fr/recherche/rncp/37306/) ; CFD `50025138` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37306). ROME : N4402 — Exploitation et manoeuvre des remontées mécaniques.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37306&target_diploma_level=3) : 2 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Remontées mécaniques, téléphériques : 0 / 11.
- Maintenance d'équipements, ascenseurs : 0 / 0.

### 84. CAP vannerie — ajout France

**Types d’entreprises :** Objets en bois, liège, vannerie.

**Lecture Onisep :** Artisans et coopératives fabriquant des objets tressés en fibres végétales.

[Fiche diplôme Onisep](https://www.onisep.fr/http/redirection/formation/slug/FOR.1136).
[RNCP37899](https://www.francecompetences.fr/recherche/rncp/37899/) ; CFD `50023438` ; [certification via LBA](https://api.apprentissage.beta.gouv.fr/api/certification/v1?identifiant.rncp=RNCP37899). ROME : B1401 — Réalisation d''objets en lianes, fibres et brins végétaux.

[Recherche LBA](https://api.apprentissage.beta.gouv.fr/api/job/v1/search?rncp=RNCP37899&target_diploma_level=3) : 0 offres retournées (0 exclues), 150 recruteurs potentiels. Répartition des résultats retenus par secteur (offres / recruteurs) :

- Objets en bois, liège, vannerie : 0 / 0.

