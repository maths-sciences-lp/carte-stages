# Domaines « parlants » pour un élève de 3e -> sous-domaines Onisep et mots du libellé
import re
DOM=[
 ('batiment','🧱','Bâtiment, travaux publics','construire, rénover, peindre, carreler',['génie civil','maçonnerie','finition','plâtrerie','charpente','travaux publics','bureau d\'études btp','architecture'],r'b[aâ]timent|ma[çc]on|peint|carrel|pl[aâ]tr|couvreur|charpent|travaux publics|g[ée]om[èe]tre|menuiserie aluminium|m[ée]tallerie|interventions sur le patrimoine'),
 ('bois','🪚','Bois, menuiserie, ameublement','fabriquer et poser des meubles, des escaliers, des cuisines',['agencement','ameublement','menuiserie','bois'],r'bois|menuis|[ée]b[ée]nis|agencement|ameublement|tapissier|charpent'),
 ('energie','⚡','Électricité, énergie, chauffage','installer, dépanner, économiser l\'énergie',['électrotechnique','énergies','équipement technique'],r'[ée]lectric|[ée]nerg|chauffage|climatis|froid|thermique|sanitaire|plomb'),
 ('numerique','💻','Numérique, réseaux, électronique','ordinateurs, réseaux, objets connectés',['informatique','électronique','télécommunications','développement','systèmes et réseaux'],r'num[ée]rique|r[ée]seaux informatiques|[ée]lectroni|informati|cybers|connect[ée]s'),
 ('auto','🔧','Mécanique, auto, moto','réparer des voitures, des motos, des engins',['automobile','cycle, moto','engins','aéronautique','machinisme agricole'],r'v[ée]hicule|automobile|moto|carrosserie|peinture en carrosserie|engin|a[ée]ronaut|mat[ée]riels'),
 ('industrie','🏭','Industrie, maintenance, métal','machines, usines, soudure, fabrication',['maintenance, qualité','métallurgie','travail des métaux','fabrication, productique','méthodes industrialisation','automatismes','céramique, composites','papier, carton','verre','matériaux','mines et carrières','fonction production','études et développement','mécanique (généralités)'],r'industri|usinage|chaudronn|soud|fonder|plastur|composite|maintenance des syst|productique|outillage|pilote de ligne|microtechn|mod[ée]l'),
 ('arts','🎨','Arts, artisanat, communication visuelle','dessiner, imprimer, créer des objets d\'art',['artisanat d\'art','arts appliqués','arts graphiques','arts plastiques','industries graphiques','audiovisuel','multimédia'],r'artisanat|m[ée]tiers d.art|graph|signal|imprim|photo|bijou|c[ée]ramique|verrier|reliure|enseigne|d[ée]cor'),
 ('commerce','🛍️','Commerce, vente, accueil','conseiller des clients, vendre, accueillir',['marketing, vente','grande distribution et petits commerces'],r'commerce|vente|relation client|accueil|vendeur|[ée]quipier polyvalent'),
 ('gestion','🗂️','Gestion, bureau, administration','organiser, gérer des dossiers, travailler en bureau',['administration de l\'entreprise','comptabilité','ressources humaines','secrétariat','sciences économiques'],r'gestion-administration|gestion administrative|administra|assistance [àa] la gestion'),
 ('cuisine','🍳','Cuisine, hôtellerie, restauration','cuisiner, servir, accueillir à l\'hôtel',['hôtellerie','restauration','tourisme'],r'cuisin|restaurant|h[ôo]tel|commercialisation et services en|serveur'),
 ('alimentation','🥖','Alimentation : boulangerie, boucherie…','pain, gâteaux, viande, poisson, chocolat',['agroalimentaire'],r'boulang|p[âa]tiss|bouch|charcut|poissonn|traiteur|chocolat|glacier|primeur|alimentation|fromag'),
 ('sante','🤝','Santé, social, aide aux personnes','s\'occuper des enfants, des personnes âgées ou malades',['travail social','paramédical','médical'],r'accompagnement|soins|petite enfance|services aux personnes|sant[ée]|optique|proth[èe]s|\\baide\\b'),
 ('beaute','💇','Coiffure, esthétique','coiffer, maquiller, prendre soin de l\'apparence',['esthétique'],r'coiff|esth[ée]tique|beaut[ée]|perruq'),
 ('transport','🚚','Transport, logistique','conduire, gérer des colis et des entrepôts',['logistique','transport'],r'logistiq|transport|conduct|livr|messagerie|op[ée]rateur'),
 ('nature','🌿','Nature, jardins, animaux, agriculture','travailler dehors, avec les plantes ou les animaux',['agriculture','cultures','forêt','soins aux animaux','élevage','aménagement paysager','protection des espaces naturels'],r'paysag|jardin|agricol|horticol|animal|[ée]levage|for[êe]t|fleur|vigne|productions'),
 ('environnement','♻️','Environnement, propreté, eau','nettoyer, recycler, traiter l\'eau',['propreté','déchets, pollutions et risques','gestion de l\'eau','environnement (généralités)','urbanisme','aménagement du territoire'],r'propret[ée]|hygi[èe]ne|d[ée]chet|\\beau\\b|environnement|recycl'),
 ('mode','👕','Mode, textile, cuir','coudre, créer des vêtements, travailler le cuir',['textile, habillement','matériaux souples'],r'mode|couture|textile|v[êe]tement|cuir|maroquin|cordonn|tapiss|habillement'),
 ('securite','🛡️','Sécurité','protéger les personnes et les lieux',['sécurité, prévention'],r's[ée]curit|pr[ée]vention'),
 ('labo','🧪','Laboratoire, chimie','faire des analyses, des expériences',['chimie','biologie'],r'laboratoire|chimi'),
]
def domaines(libelle,indexation):
    subs=[d.split('/',1)[1].strip().lower() for d in indexation.split('|') if '/' in d]
    out=[]
    for k,_,_,_,S,rx in DOM:
        if any(any(s.startswith(x.lower()) or x.lower()==s for x in S) for s in subs) or re.search(rx,libelle,re.I): out.append(k)
    return out
