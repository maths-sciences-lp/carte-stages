# Domaines de stage -> secteurs -> codes d'activité (NAF rév. 2).
# Un secteur = un groupe d'entreprises qu'un élève comprend ; les codes viennent de la nomenclature Insee.
DOMAINES = {
 "Bâtiment et travaux publics": {
  "Construction, maçonnerie, gros œuvre": ["41.20A", "41.20B", "43.99C", "43.91A", "43.91B", "43.99A", "23.70Z"],
  "Travaux publics, routes, réseaux": ["42.11Z", "42.13A", "42.21Z", "42.99Z", "43.12A", "43.12B"],
  # 42.22Z séparé des travaux publics (filière énergie, 8/10/2026) : seule partie utile
  # aux électriciens et à la 2de TNE ; les formations des travaux publics gardent les deux.
  "Réseaux électriques et télécoms": ["42.22Z"],
  # Sans code propre (9/10/2026) : services routiers de l'État tirés de « Mairies,
  # administrations » par leur SIREN (voir ROUTES_ETAT_SIREN) ; postes de trafic exclus.
  "Routes de l'État : études et districts": [],
  "Routes de l'État : centres d'entretien": [],
  "Peinture, plâtre, carrelage, sols, isolation": ["43.31Z", "43.33Z", "43.34Z", "43.39Z", "43.29A"],
  # Ancienne « Menuiserie, agencement, serrurerie » séparée le 9/10/2026 (filière bois,
  # 10 entreprises vérifiées par code) : 43.32B et 25.12Z sont du métal 10 fois sur 10.
  "Menuiserie bois, agencement": ["43.32A", "43.32C", "16.23Z"],
  "Menuiserie métallique, serrurerie": ["43.32B", "25.12Z"],
  "Géomètres-experts, topographie": ["71.12A"],
  "Architectes": ["71.11Z"],
  # 74.90A séparé le 8/10/2026 (10 entreprises vérifiées, toutes du bâtiment) ; 71.12B reste
  # seul ici : 20 vérifiées, la moitié seulement dans le bâtiment (le reste industrie, conseil).
  "Bureaux d'études, économistes de la construction": ["71.12B"],
  "Économistes de la construction": ["74.90A"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Éléments préfabriqués en béton": ["23.61Z"],
 },
 "Énergie, électricité, chauffage": {
  "Électricité du bâtiment": ["43.21A", "43.21B"],
  "Plomberie, chauffage, climatisation, froid": ["43.22A", "43.22B", "35.30Z"],
  # Découpée le 8/10/2026 (filière énergie, 10 entreprises vérifiées par code) : restent ici
  # ascensoristes et portes automatiques (43.29B), réparation de moteurs et matériel électrique
  # (33.14Z) et installation d'équipements électriques (33.20D), utiles aux électriciens.
  "Maintenance d'équipements, ascenseurs": ["33.14Z", "33.20D", "43.29B"],
  # 33.20B : surtout des frigoristes (froid industriel, groupes de camions), aussi des machines.
  "Froid industriel, installation de machines": ["33.20B"],
  "Production et distribution d'énergie": ["35.11Z", "35.13Z", "35.14Z", "35.22Z"],
 },
 "Automobile, moto, poids lourds, aéronautique": {
  "Garages, carrosseries (voitures)": ["45.20A"],
  "Poids lourds, utilitaires": ["45.20B"],
  "Motos, scooters": ["45.40Z"],
  "Concessionnaires, vente de véhicules et pièces": ["45.11Z", "45.19Z", "45.31Z", "45.32Z"],
  "Aéronautique": ["30.30Z", "33.16Z"],
 },
 "Industrie, mécanique, métallerie": {
  "Usinage, mécanique, outillage": ["25.62A", "25.62B", "25.73A", "25.73B", "28.41Z", "28.99B", "33.11Z"],
  "Chaudronnerie, soudure, structures métalliques": ["25.11Z", "25.29Z", "25.99B"],
  "Électronique, matériel électrique": ["26.11Z", "26.12Z", "27.11Z", "27.12Z", "27.40Z", "27.90Z"],
  # Sorti de « Maintenance d'équipements, ascenseurs » (8/10/2026) : machines agricoles, engins,
  # hydraulique (33.12Z), électronique et optique (33.13Z), contrôle industriel (33.20C).
  "Réparation de machines et d'électronique": ["33.12Z", "33.13Z", "33.20C"],
  "Plastique, verre, matériaux": ["22.21Z", "22.22Z", "22.29A", "22.29B", "23.12Z", "23.19Z"],
  "Chimie, pharmacie, cosmétiques, papier": ["20.11Z", "20.13B", "20.14Z", "20.16Z", "20.30Z", "20.41Z", "20.42Z", "20.59Z", "21.10Z", "21.20Z", "17.12Z", "17.21A", "17.21B", "17.29Z"],
  "Laboratoires d'analyses et d'essais": ["71.20B"],
  "Industrie agroalimentaire": ["10.13A", "10.39B", "10.51C", "10.72Z", "10.73Z", "10.85Z", "10.89Z", "11.07A", "11.07B"],
  "Bateaux, nautisme": ["30.12Z", "33.15Z"],
  "Matériels agricoles, engins de chantier": ["28.30Z", "28.92Z", "46.61Z", "46.63Z", "77.31Z", "77.32Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Fonderies": ["24.51Z", "24.52Z", "24.53Z", "24.54Z"],
  "Optique, photonique, instruments de mesure": ["26.70Z", "26.51B"],
  "Construction de navires": ["30.11Z"],
  "Laboratoires de recherche scientifique": ["72.11Z", "72.19Z"],
  "Armurerie, fabrication d’armes": ["25.40Z"],
  "Transformation de viandes": ["10.11Z", "10.12Z"],
  "Transformation de poissons, crustacés, mollusques": ["10.20Z"],
 },
 "Bois, ameublement, métiers d'art": {
  "Ébénisterie, meubles, restauration de meubles": ["31.01Z", "31.02Z", "31.09A", "31.09B", "95.24Z"],
  "Tapisserie, décoration textile": ["13.92Z", "47.53Z"],
  "Bijouterie, horlogerie": ["32.12Z", "32.13Z", "95.25Z"],
  "Céramique, verre d'art, instruments de musique": ["23.41Z", "23.13Z", "32.20Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Scieries, préparation du bois": ["16.10A", "16.10B"],
  "Objets en bois, liège, vannerie": ["16.29Z"],
  "Fabrication de monnaies, médailles": ["32.11Z"],
 },
 "Communication visuelle, impression, audiovisuel": {
  "Imprimerie, prépresse, reliure": ["18.11Z", "18.12Z", "18.13Z", "18.14Z"],
  "Enseignes, signalétique, marquage": [],
  # 74.10Z séparé le 9/10/2026 (filière arts graphiques) : 20 entreprises vérifiées, surtout
  # des architectes d'intérieur, aucun fabricant d'enseignes.
  "Publicité, design graphique": ["73.11Z", "73.12Z"],
  "Design d'intérieur et d'objet": ["74.10Z"],
  "Photographie": ["74.20Z"],
  "Audiovisuel, cinéma, son": ["59.11A", "59.11B", "59.11C", "59.12Z", "59.20Z", "60.20A"],
 },
 "Commerce et vente": {
  "Supermarchés, grandes surfaces": ["47.11B", "47.11C", "47.11D", "47.11F"],
  "Supérettes, alimentation générale": ["47.11A", "47.11E", "47.29Z"],
  "Vêtements, chaussures, accessoires": ["47.71Z", "47.72A", "47.72B", "47.77Z"],
  "Magasins spécialisés (bricolage, maison, sport, high-tech…)": ["47.41Z", "47.42Z", "47.43Z", "47.52A", "47.52B", "47.54Z", "47.59A", "47.59B", "47.61Z", "47.62Z", "47.64Z", "47.65Z", "47.78C"],
  "Commerce de gros (entre entreprises)": ["46.39B", "46.43Z", "46.49Z", "46.51Z", "46.69B", "46.73A", "46.74B", "46.90Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Grossistes en viandes": ["46.32A", "46.32B"],
  "Grossistes en poissons, crustacés, mollusques": ["46.38A"],
  "Grossistes en fruits et légumes": ["46.31Z"],
 },
 "Alimentation, métiers de bouche": {
  "Boulangerie, pâtisserie": ["10.71C", "10.71D", "47.24Z"],
  "Boucherie, charcuterie, poissonnerie": ["47.22Z", "10.13B", "47.23Z"],
  "Traiteurs": ["56.21Z"],
  "Chocolaterie, confiserie, glaces": ["10.82Z", "10.52Z"],
  "Primeur, fromagerie, épicerie fine, cave": ["47.21Z", "47.25Z", "47.29Z"],
 },
 "Hôtellerie, restauration": {
  "Restaurants": ["56.10A", "56.10B"],
  "Restauration rapide": ["56.10C"],
  "Cafés, bars": ["56.30Z"],
  "Hôtels": ["55.10Z", "55.20Z"],
  "Restauration collective (cantines, entreprises)": ["56.29A", "56.29B"],
 },
 "Santé, social, aide à la personne": {
  "Crèches, petite enfance": ["88.91A"],
  "Personnes âgées (EHPAD, résidences)": ["87.10A", "87.30A"],
  "Handicap (foyers, ESAT, IME)": ["87.10B", "87.10C", "87.20A", "87.30B", "88.10C", "88.91B"],
  "Aide à domicile": ["88.10A", "88.10B"],
  "Hôpitaux, cliniques, laboratoires": ["86.10Z", "86.90B"],
  "Ambulances": ["86.90A"],
  "Pharmacie, optique, prothèses": ["47.73Z", "47.74Z", "47.78A", "32.50A", "32.50B"],
 },
 "Coiffure, esthétique, bien-être": {
  "Coiffure": ["96.02A"],
  "Esthétique, soins de beauté": ["96.02B", "96.04Z"],
  "Parfumerie, cosmétiques": ["47.75Z"],
 },
 "Transport, logistique": {
  "Transport de marchandises, livraison": ["49.41A", "49.41B", "49.41C", "53.20Z"],
  "Entrepôts, logistique": ["52.10B", "52.24B", "52.29A", "52.29B"],
  "Transport de voyageurs": ["49.31Z", "49.32Z", "49.39A", "49.39B"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Navigation maritime, plaisance professionnelle": ["50.10Z", "50.20Z"],
  "Navigation fluviale": ["50.30Z", "50.40Z"],
  "Remontées mécaniques, téléphériques": ["49.39C"],
  "Déménagement": ["49.42Z"],
  "Poste, courrier": ["53.10Z"],
 },
 "Gestion, administration, accueil": {
  "Comptabilité, conseil, gestion": ["69.20Z", "70.22Z", "69.10Z"],
  "Mairies, administrations": ["84.11Z", "84.12Z", "84.13Z"],
  # Sans code propre : écoles publiques rangées ici depuis « Mairies, administrations »
  # quand leur activité est 85.10Z ou 85.20Z (voir ECOLES_NAF) ; pas de collecte en plus.
  "Écoles maternelles et élémentaires": [],
  # Sans code propre (8/10/2026) : établissements de « Mairies, administrations » dont le
  # propriétaire est une collectivité ou une intercommunalité et l'activité propre 84.11Z,
  # 84.13Z ou 81.10Z (mairies, services, centres techniques). Voir COMMUNES_NAF.
  "Communes et intercommunalités": [],
  "Banques, assurances": ["64.19Z", "65.12Z", "66.22Z"],
  "Agences immobilières, gestion de logements": ["68.31Z", "68.32A", "68.20A"],
  "Secrétariat, accueil, centres d'appels": ["82.11Z", "82.19Z", "82.20Z", "82.30Z"],
  "Intérim, recrutement": ["78.10Z", "78.20Z", "78.30Z"],
 },
 "Sécurité": {
  "Sécurité privée, surveillance": ["80.10Z", "80.20Z"],
 },
 "Propreté, environnement": {
  "Nettoyage, propreté": ["81.21Z", "81.22Z", "81.29A", "81.29B"],
  "Déchets, recyclage, assainissement": ["38.11Z", "38.12Z", "38.21Z", "38.32Z", "37.00Z", "39.00Z"],
  "Eau potable (captage, traitement, distribution)": ["36.00Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Traitement des déchets dangereux": ["38.22Z"],
 },
 "Espaces verts, agriculture, animaux": {
  "Paysagistes, espaces verts": ["81.30Z"],
  "Fleuristes, jardineries": ["47.76Z"],
  "Horticulture, maraîchage, agriculture": ["01.13Z", "01.19Z", "01.30Z", "01.11Z", "01.50Z"],
  "Vétérinaires, soins aux animaux": ["75.00Z", "96.09Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Travaux agricoles, services aux cultures": ["01.61Z"],
  "Cultures spécialisées, vergers, cultures tropicales": ["01.12Z", "01.14Z", "01.22Z", "01.23Z", "01.24Z", "01.25Z", "01.26Z", "01.27Z", "01.28Z", "01.29Z"],
  "Élevage bovin, ovin, caprin, porcin, volailles": ["01.41Z", "01.42Z", "01.45Z", "01.46Z", "01.47Z"],
  "Élevage de chevaux, haras": ["01.43Z"],
  "Autres élevages (dont animaux de compagnie, apiculture)": ["01.49Z"],
  "Services à l'élevage, maréchalerie": ["01.62Z"],
  "Viticulture, vinification": ["01.21Z", "11.02A", "11.02B"],
  "Forêts, travaux forestiers": ["02.10Z", "02.20Z", "02.40Z"],
  "Aquaculture, pisciculture, conchyliculture": ["03.21Z", "03.22Z"],
  "Pêche professionnelle": ["03.11Z", "03.12Z"],
 },
 "Informatique, numérique, télécoms": {
  "Réparation d'ordinateurs et de téléphones": ["95.11Z", "95.12Z"],
  # 62.02A (conseil en systèmes et logiciels) retiré le 8/10/2026 : 10 entreprises vérifiées,
  # 8 consultants (souvent seuls) ou sociétés d'ingénieurs, aucun technicien (voir CODES_RETIRES).
  "Services informatiques, réseaux": ["62.01Z", "62.03Z", "62.09Z"],
  "Télécommunications": ["61.10Z", "61.20Z", "61.90Z"],
 },
 "Mode, textile, cuir": {
  "Couture, confection": ["14.13Z", "14.14Z", "14.19Z", "13.30Z"],
  "Cuir, maroquinerie, cordonnerie": ["15.12Z", "15.20Z", "95.23Z"],
  "Pressing, blanchisserie, retouches": ["96.01A", "96.01B", "95.29Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Fleurs artificielles, parures de mode": ["32.99Z"],
 },
 "Sport, animation, culture": {
  "Clubs et salles de sport": ["93.11Z", "93.12Z", "93.13Z"],
  "Loisirs, animation": ["93.29Z", "93.21Z", "88.99B"],
  "Spectacle, musées, bibliothèques": ["90.01Z", "90.02Z", "90.04Z", "91.01Z", "91.02Z"],
  "Associations (animation, solidarité)": ["94.99Z"],
  # ajout France — sources et limites : formation_secteurs_france.json
  "Parcs naturels, jardins botaniques et zoologiques": ["91.04Z"],
  "Activités sportives (dont écuries de course)": ["93.19Z"],
  "Guides, offices de tourisme": ["79.90Z"],
  "Enseignement culturel, conservatoires": ["85.52Z"],
  "Écoles de sport, équitation": ["85.51Z"],
 },
}

# Repérage par le nom ou l'enseigne : complète un secteur avec des entreprises classées ailleurs
# (sources limitées aux domaines techniques, pour éviter « Lissac Enseigne », chaîne d'opticiens)
SOURCES_MOTS_CLES = ["Bâtiment et travaux publics", "Énergie, électricité, chauffage", "Industrie, mécanique, métallerie",
 "Bois, ameublement, métiers d'art", "Communication visuelle, impression, audiovisuel"]
MOTS_CLES = {
 # Sans « signalisation » ni marquage routier, au sol ou de parking (9/10/2026) : ce sont
 # des entreprises de travaux publics, pas de signalétique graphique.
 "Enseignes, signalétique, marquage": r"^(?!.*\b(?:ROUTI\w*|SOLS?|PARKINGS?|CHAUSSEES?|VOIRIES?)\b).*\b(ENSEIGNES?|SIGNALETIQUES?|MARQUAGES?|COVERING|ADHESIFS?|LETTRAGES?|SERIGRAPH\w*|STICKERS?|PLV|GRAVURES?)\b",
 # Noms en aluminium, métal ou serrurerie exclus : ils relèvent de la menuiserie métallique.
 "Menuiserie bois, agencement": r"^(?!.*\b(?:ALU\w*|METALL\w*|SERRUR\w*|FERRONN\w*|ACIER)\b).*\b(AGENCEMENTS?|AGENCEUR|MENUISERIES?|MENUISIER|EBENISTERIE|EBENISTE)\b",
 "Plomberie, chauffage, climatisation, froid": r"\b(CHAUFFAGE|CLIMATISATION|CLIMATIQUE|THERMIQUE|PLOMBERIE|PLOMBIER|FRIGORIFIQUE|POMPES? A CHALEUR)\b",
 "Géomètres-experts, topographie": r"\b(GEOMETRES?|TOPOGRAPH\w*)\b",
}

# Types où seuls les noms qui correspondent sont gardés : le code 71.20B mêle les
# laboratoires et les bureaux de contrôle ou de diagnostic immobilier.
FILTRES = {
 # ajout France : 32.99Z couvre aussi de nombreux objets sans rapport avec la mode.
 "Fleurs artificielles, parures de mode": r"FLEUR|FLORAL|PLUMASS|PARUR",
 # 96.04Z (entretien corporel) contient aussi les bains-douches municipaux : ni les
 # bains-douches ni les communes ne relèvent de l'esthétique (octobre 2026, audit Codex).
 "Esthétique, soins de beauté": r"^(?!.*BAINS?[ -]DOUCHES)(?!(?:VILLE|COMMUNE) D)",
 "Laboratoires d'analyses et d'essais": r"LABO|ANALY|ESSAI|MESUR|METROLOG|EUROFINS|\bSGS\b|VERITAS|INTERTEK|EMITECH|CHIMI|MICROBIO|BACTERIO|HYGIENE ALIMENT|POLLUANT|TOXICO|WESSLING|\bALS\b|CONTROLE QUALITE|\bLNE\b",
}

# Écoles publiques : leur commune les fait entrer dans « Mairies, administrations » (repli sur
# l'activité de l'unité légale, 84.11Z), alors que leur propre activité est l'enseignement.
# Elles vont dans « Écoles maternelles et élémentaires », reliée aux mêmes formations que les
# mairies, sauf géomètre et bâtiment, pour qui une école n'est pas un lieu de stage (audit du 8/10/2026).
ECOLES_NAF = ('85.10Z', '85.20Z')
ECOLES_EXCLUES = (
    'bac-pro-geometre',
    'bac-pro-technicien-d-etudes-du-batiment-option-a-etudes-et-e',
    'bac-pro-technicien-d-etudes-du-batiment-option-b-assistant-e',
    'cap-interventions-en-maintenance-technique-des-batiments',
    '2nde-etudes-et-modelisation-numerique-du-batiment-emnb',
)

# Lieux sans personnel (filière énergie, 8/10/2026) : l'activité est la bonne, mais ce sont
# des comptes de collectivités (lotissements, zones d'activité, remembrement en 42.99Z ;
# panneaux solaires communaux en 35.11Z) ou des fermes qui vendent leur électricité solaire.
# Retirés quand l'activité propre est dans la liste et que le propriétaire est une personne
# publique (catégorie juridique 7…) ou une exploitation agricole (activité 01 à 03).
SANS_PERSONNEL = {
    "Travaux publics, routes, réseaux": {"42.99Z": ("public",)},
    "Production et distribution d'énergie": {"35.11Z": ("public", "agricole")},
}


# Catégories issues du découpage d'une catégorie plus ancienne : sert aux contrôles qui
# comparent avec les tables historiques (rien n'est retiré aux formations d'origine).
DECOUPAGES = {
    "Écoles maternelles et élémentaires": "Mairies, administrations",
    "Réseaux électriques et télécoms": "Travaux publics, routes, réseaux",
    "Froid industriel, installation de machines": "Maintenance d'équipements, ascenseurs",
    "Réparation de machines et d'électronique": "Maintenance d'équipements, ascenseurs",
    "Communes et intercommunalités": "Mairies, administrations",
    "Routes de l'État : études et districts": "Mairies, administrations",
    "Routes de l'État : centres d'entretien": "Mairies, administrations",
    "Économistes de la construction": "Bureaux d'études, économistes de la construction",
    "Menuiserie bois, agencement": "Menuiserie, agencement, serrurerie",
    "Menuiserie métallique, serrurerie": "Menuiserie, agencement, serrurerie",
    "Design d'intérieur et d'objet": "Publicité, design graphique",
}

# Communes et intercommunalités : activité propre et catégorie juridique du propriétaire
# (72… collectivités territoriales, 734…/735… intercommunalités et syndicats).
COMMUNES_NAF = ('84.11Z', '84.13Z', '81.10Z')
COMMUNES_CJ = ('72', '734', '735')

# Codes retirés d'une catégorie après vérification : les établissements publiés qui n'y
# étaient que par ce code en sortent (stage_reclasser_naf.py).
CODES_RETIRES = {
    "Services informatiques, réseaux": ["62.02A"],
}

# Services routiers de l'État (9/10/2026, d'après la vérification de Codex, note 84.13Z) :
# les 10 directions interdépartementales des routes, et en Île-de-France la partie routière
# de la DRIEAT (sites AGER, CEI, UER, SGPR, DIRIF). Le code 84.13Z seul ne suffit pas : il
# couvre aussi France Travail, le tourisme, les agences de l'eau. Selon le nom du site :
# centres d'entretien et d'intervention ; postes de trafic (restent dans les mairies) ;
# sinon études, ingénierie, districts et sièges.
ROUTES_ETAT_SIREN = ('130001712', '130001738', '130001688', '130001530', '130001563',
                     '130001761', '130001571', '130001696', '130001704', '130001670')
ROUTES_DRIEAT = ('130029325', r'\b(AGER|CEI|UER|SGPR|DIRIF)\b')
ROUTES_ENTRETIEN = r'\bPA\b|PO[IN]NT D.?APPUI|POINT APPUI|LOGISTIQUE|\bCEI\w*|\bCES\b|\bUER\b|\bAGER\b|\bENTR\w*|INTERV|TRAVAUX|EQUIPES'
ROUTES_ETUDES = r'DISTRICT|\bSIR\b'
ROUTES_TRAFIC = r'\bPC\b|CIGT|TRAFIC|CRICR'
