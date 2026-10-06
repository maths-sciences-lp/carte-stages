"""Rend les adresses Sirene lisibles : « 26 avenue du General de Gaulle, 93170 Bagnolet » + repère (« chez Auchan, centre commercial Bel Est »)."""
import re
TYPES={'RUE':'rue','AV':'avenue','AVENUE':'avenue','BD':'boulevard','BOULEVARD':'boulevard','PL':'place','PLACE':'place','ALL':'allée','ALLEE':'allée',
 'CHE':'chemin','CHEMIN':'chemin','IMP':'impasse','IMPASSE':'impasse','QU':'quai','QUAI':'quai','RTE':'route','ROUTE':'route','SQ':'square','SQUARE':'square',
 'PAS':'passage','PASS':'passage','PASSAGE':'passage','CRS':'cours','COURS':'cours','VOIE':'voie','SEN':'sente','SENTE':'sente','VLA':'villa','VILLA':'villa',
 'CI':'cité','CITE':'cité','PRV':'parvis','PARVIS':'parvis','ESP':'esplanade','ESPLANADE':'esplanade','PROM':'promenade','PROMENADE':'promenade',
 'RPT':'rond-point','CHS':'chaussée','CHAUSSEE':'chaussée','HAM':'hameau','HAMEAU':'hameau','FG':'faubourg','FBG':'faubourg','FAUBOURG':'faubourg','PONT':'pont','PORT':'port','MAIL':'mail'}
ABBR=[(r'\bC\s?CIAL\b|\bCTRE\s+CIAL\b|\bCENTRE\s+CIAL\b|\bCCIAL\b|\bCC\b','CENTRE COMMERCIAL'),(r'\bZI\b','ZONE INDUSTRIELLE'),(r'\bZAE?\b',"ZONE D'ACTIVITES"),
 (r'\bLD\b|\bLIEUDIT\b|\bLIEU DIT\b','LIEU-DIT'),(r'\bBAT\b','BATIMENT'),(r'\bRES\b','RESIDENCE'),(r'\bST\b','SAINT'),(r'\bSTE\b','SAINTE'),(r'\bCS\s*\d+\b',''),(r'\bCEDEX\b(\s*\d+)?',''),(r'\bBP\s*\d+\b','')]
PETITS={'de','du','des','la','le','les','et','à','au','aux','en','sur','sous','d','l','chez'}
def _cap(w,first):
    if not w: return w
    if '-' in w: return '-'.join(_cap(p,first and i==0) for i,p in enumerate(w.split('-')))
    lw=w.lower()
    if re.match(r"^[ld]'",lw): return lw[:2]+_cap(lw[2:],True)
    if lw in ('zac','zad','zup'): return lw.upper()
    if re.match(r'^\d',lw): return lw
    if lw in PETITS and not first: return lw
    return lw[:1].upper()+lw[1:]
def titre(s,debut=True):
    ws=s.split(); return ' '.join(_cap(w,debut and i==0) for i,w in enumerate(ws))
TYP='|'.join(sorted(TYPES,key=len,reverse=True))
RX=re.compile(r'(?:(\d+(?:\s?(?:BIS|TER|QUATER|[A-Z])\b)?)\s+)?\b('+TYP+r')\b(?!.*\b\d+[A-Z]?\s+(?:'+TYP+r')\b)\s+(.+?)\s+(\d{5})\s+(.+)$')
MOTS_VIDES={'GRANDE','GRAND','PETITE','PETIT','VIEUX','BIS','TER','APPARTEMENT','APPT','APT','APP','RDC','REZ-DE-CHAUSSEE','HALL','CENTRA','CELLULE',
 'ESC','ESCALIER','LOGEMENT','NUMERO','ETG','TSA','MAISON','PARIS','FRANCE','LOT','CAP','PAVILLON'}
IND={'B':'bis','BIS':'bis','T':'ter','TER':'ter','Q':'quater','QUATER':'quater','C':'quinquies'}
def numero(n):
    """« 12 B » -> « 12 bis », « 114 T » -> « 114 ter », « 12 A » -> « 12 A »."""
    m=re.fullmatch(r'(\d+)\s?(BIS|TER|QUATER|[A-Z])?',n)
    if not m or not m.group(2): return n
    return m.group(1)+' '+IND.get(m.group(2),m.group(2))
def nettoie(a):
    a=re.sub(r'\s+',' ',(a or '').upper()).strip()
    for rx,rep in ABBR: a=re.sub(rx,rep,a)
    a=re.sub(r'\s+',' ',a).strip()
    m=RX.search(a)  # la dernière rue numérotée l'emporte
    cp_ville=re.search(r'(\d{5})\s+(.+)$',a)
    if m:
        num,typ,nom,cp,ville=m.groups()
        rue=((numero(num)+' ') if num else '')+TYPES[typ]+' '+titre(nom,False)
        avant=a[:m.start()].strip()
        if not num: avant=re.sub(r'\b\d+[A-Z]?$','',avant).strip()
        principal=f'{rue}, {cp} {titre(ville)}'
    elif cp_ville:
        avant=a[:cp_ville.start()].strip(); cp,ville=cp_ville.groups()
        principal=(titre(avant)+', ' if avant else '')+f'{cp} {titre(ville)}'; avant=''
    else:
        return titre(a),''
    # repère : sans numéros isolés, sans code postal répété, sans « ET »
    avant=re.sub(r'\b\d{5}\s+\S+(-\S+)*','',avant)
    avant=re.sub(r'(^|\s)[\d\-/ ]+(?=\s|$)',' ',avant)
    avant=re.sub(r'\s+',' ',avant).strip(' -,')
    if re.fullmatch(r"(ET|ANGLE|LIEU-DIT|UNIT|LOCAL|LOT|BUREAU|BATIMENT|ETAGE|BOITE|PORTE)?",avant): avant=''
    # reste sans sens pour un élève : lettres isolées ou sigles de 2 lettres (« A », « AU », « RN », « CD », « CX »…)
    if all(len(w)<=2 for w in avant.replace('-',' ').split()): avant=''
    # un seul mot qui ne situe rien (étage, appartement, « grande »…) : on n'affiche pas
    if len(avant.split())==1 and (re.search(r'\d',avant) or avant in MOTS_VIDES): avant=''
    rep=titre(avant)
    for g in ('Centre Commercial','Zone Industrielle',"Zone d'Activites",'Lieu-Dit'): rep=rep.replace(g,g.lower())
    if rep: rep=rep[0].upper()+rep[1:]
    return principal,rep
if __name__=='__main__':
    for t in ['3 RUE JEAN JAURES 93170 BAGNOLET','LIEUDIT AVENUE GALLIENI 2 AVENUE DU GENERAL DE GAULLE 93170 BAGNOLET','4-14 4 RUE SADI CARNOT 93170 BAGNOLET',
              'CHEZ AUCHAN CCIAL BEL EST 26 AVENUE DU GENERAL DE GAULLE 93170 BAGNOLET','91270 VIGNEUX-SUR-SEINE 37 RUE DE LA LONGUERAIE 91270 VIGNEUX-SUR-SEINE',
              '45 BD CHANZY 294 AVENUE ARISTIDE BRIAND 93320 LES PAVILLONS-SOUS-BOIS','UNIT 70A AVENUE DU LUXEMBOURG 94320 THIAIS','AVENUE HENRI BARBUSSE 95670 MARLY-LA-VILLE',
              "41 RUE DE L'ECHIQUIER 75010 PARIS",'87 RUE SAINT-LAZARE 75009 PARIS','13 CHEMIN DES CHAUDRONNIERS 94310 ORLY','ZI DES CHANOUX 93330 NEUILLY-SUR-MARNE',
              'MAIRIE 1 PL DE LA REPUBLIQUE 93100 MONTREUIL','30-32 30 RUE JEANNE HORNET 93170 BAGNOLET','CTRE CIAL BEL EST 28 AVENUE DU GENERAL DE GAULLE 93170 BAGNOLET',
              '210 RUE SADI CARNOT 93170 BAGNOLET','5 RUE ST HONORE 75001 PARIS 1','TOUR FRANKLIN 100 TERRASSE BOIELDIEU 92800 PUTEAUX']:
        print(t,'\n   →',nettoie(t))
