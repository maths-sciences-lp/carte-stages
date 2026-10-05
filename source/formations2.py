import json,collections
o=json.load(open('onisep_formations.json')); f=json.load(open('formations_idf.json'))
byname={x['libelle_formation_principal']:x for x in o}
# (type, abrégé) -> (nom complet, nom Onisep pour domaine/lien ou None, domaine manuel)
M={('CAP','OPERATEUR/OPERATRICE LOGISTIQUE'):('CAP opérateur, opératrice logistique',)*2,
 ('BAC','LOGISTIQUE'):('bac pro métiers de la logistique',)*2,
 ('BAC','MAINTEN. ET EFFICACITE ENERGETIQ.'):('bac pro maintenance et efficacité énergétique',)*2,
 ('CAP','OUTILLAGES A DECOUPER ET EMBOUTIR'):('CAP outillages en outils à découper et à emboutir',None,'mécanique'),
 ('BAC','METIERS DE LA MODE - VÊTEMENT'):('bac pro métiers de la mode – vêtement',None,'mode, textile'),
 ('CAP',"AGENT DE PROPRETE ET D'HYGIENE"):("CAP agent de propreté et d'hygiène",None,'propreté, hygiène'),
 ('BAC','TECHNICIEN BAT. : ORG.REAL.GROS O'):('bac pro organisation et réalisation du gros oeuvre',)*2,
 ('BAC','MAINT.VEHIC.OPTA VOIT.PARTICUL.'):('bac pro maintenance des véhicules option véhicules légers',)*2,
 ('CAP','MAINT.VEHIC.OPTA VOIT.PARTICUL.'):('CAP maintenance des véhicules option véhicules légers',)*2,
 ('BAC','HYGIENE PROPRETE STERILISATION'):('bac pro hygiène, propreté, stérilisation',)*2,
 ('BAC','MAINT.VEHIC.OPTC MOTOCYCLES'):('bac pro maintenance des véhicules option motocycles',)*2,
 ('CAP','MAINT.VEHIC.OPTC MOTOCYCLES'):('CAP maintenance des véhicules option motocycles',)*2,
 ('BAC','CONDUCT. TRANSP.ROUT.MARCHANDISES'):('bac pro conducteur routier de marchandises',)*2,
 ('BAC','REPARATION DES CARROSSERIES'):('bac pro carrossier peintre automobile',)*2,
 ('CAP','SERVICES'):('CAP agricole – services (intitulé à préciser)',None,'agriculture'),
 ('BAC','AMENAGEMENTS PAYSAGERS'):('bac pro aménagements paysagers',)*2,
 ('CAP',"METIERS DE L'AGRICULTURE"):("CAPa métiers de l'agriculture",)*2,
 ('CAP','JARDINIER PAYSAGISTE'):('CAPa jardinier-paysagiste',)*2,
 ('CAP','PRODUCTION'):('CAP agricole – production (intitulé à préciser)',None,'agriculture'),
 ('BAC','CONSTRUCTION DES CARROSSERIES'):('bac pro construction et aménagement de véhicules',)*2,
 ('BAC','LABORATOIRE CONTROLE QUALITE'):('bac pro laboratoire contrôle qualité',)*2,
 ('BAC','MAINT.VEHIC.OPTB VEHIC.TRANS.ROUT'):('bac pro maintenance des véhicules option véhicules de transport routier',)*2,
 ('CAP','MAINT.VEHIC.OPTB VEHIC.TRANS.ROUT'):('CAP maintenance des véhicules option véhicules de transport routier',)*2,
 ('CAP','COND.ENGINS TVX PUBLICS&CARRIERES'):("CAP conducteur d'engins de travaux publics et carrières",)*2,
 ('BAC','TEC CONS VTE UNIVERS JARDINERIE'):('bac pro technicien conseil vente univers jardinerie',)*2,
 ('BAC','TECHNICIEN GEOMETRE-TOPOGRAPHE'):('bac pro géomètre',)*2,
 ('CAP','CONDUCTEUR LIVREUR MARCHANDISES'):('CAP conducteur livreur de marchandises',None,'transport, logistique'),
 ('CAP','CONDUCTEUR ROUTIER MARCHANDISES'):('CAP conducteur routier de marchandises',"CAP conducteur routier de marchandises option livraisons de proximité"),
 ('CAP','CONSTR. RESEAUX CANALISATIONS TP'):('CAP constructeur de réseaux de canalisations de travaux publics',)*2,
 ('CAP','CONSTR. ROUT. ET  AMENAGT URB.'):("CAP constructeur de routes et d'aménagements urbains",)*2,
 ('CAP','PROPR.ENVIR.URBAIN-COLLEC.RECYCL'):('CAP valorisation des matières et propreté des espaces urbains',)*2,
 ('BAC','GEST. POLLUTIONS PROTEC. ENVIRON.'):("bac pro gestion des pollutions et protection de l'environnement",None,'environnement'),
 ('CAP','EMPLOYE TECHNIQUE DE LABORATOIRE'):('CAP employé technique de laboratoire',None,'chimie, biologie'),
 ('BAC','CONDUITE PRODUCTIONS HORTICOLES'):('bac pro conduite de productions horticoles (arbres, arbustes, fruits, fleurs, légumes)',)*2,
 ('BAC','TEC CONS VTE ALIMENTATION (PAB)'):('bac pro technicien conseil vente en alimentation (produits alimentaires et boissons)',)*2}
F={}
for x in f:
    m=M.get((x['type'],x['nom']))
    if m:
        x['nom']=m[0]; x['abrege']=''
        src=byname.get(m[1]) if len(m)>1 and m[1] else None
        if src: x['domaine']=src['domainesous-domaine']; x['onisep']=src['url_et_id_onisep']
        elif len(m)>2: x['domaine']=m[2]+'/'
    k=(x['type'],x['nom'])
    if k in F:
        y=F[k]; y['lycees']+=x['lycees']; y['eleves']+=x['eleves']; y['deps']=' '.join(sorted(set((y['deps']+' '+x['deps']).split())))
        y['domaine']=y['domaine'] or x['domaine']; y['onisep']=y['onisep'] or x['onisep']
    else: F[k]=x
out=list(F.values())
for x in out:
    x['dom']=x['domaine'].split('|')[0].split('/')[0].strip() if x['domaine'] else ''
    x['sous']=' ; '.join(sorted({p.split('/')[1].strip() for p in x['domaine'].split('|') if '/' in p and p.split('/')[1].strip()}))
json.dump(out,open('formations_idf.json','w'),ensure_ascii=False)
print(collections.Counter(x['type'] for x in out)); print(collections.Counter(x['dom'] for x in out if x['type']!='2NDE').most_common(40))
print([x['nom'] for x in out if x['type']!='2NDE' and not x['dom']])
