"""« Qui peut m'aider ? » : lieux d'aide aux jeunes de l'académie de Créteil (77, 93, 94),
et bibliothèques pour travailler au calme (voir plus bas).

Missions locales, CIO et Info Jeunes : annuaire de l'administration (Service-public.fr, DILA),
API api-lannuaire.service-public.fr. Les noms des agents (affectation_personne) ne sont jamais lus.
Maisons des adolescents : absentes de cet annuaire (le type « mda » y désigne les maisons de
l'autonomie) ; liste de l'ARS Île-de-France, fiches de l'Association nationale des maisons des
adolescents (anmda.fr).

Lancer depuis un dossier qui contient colleges.json (annuaire de l'Éducation nationale) :
    python3 aide.py   -> aide.json, à copier dans aide/
"""
import json, os, re, urllib.parse, urllib.request

API = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/exports/json'
CHAMPS = 'id,nom,pivot,adresse,telephone,site_internet,plage_ouverture,code_insee_commune,url_service_public,date_modification'
TYPES = {'cio': 'cio', 'mission_locale': 'ml', 'cij': 'ij'}
DEPS = {'77': 'Seine-et-Marne', '93': 'Seine-Saint-Denis', '94': 'Val-de-Marne'}

# Vérifiées le 7 octobre 2026 sur les fiches anmda.fr citées par l'ARS Île-de-France.
MDA = [
    dict(n='Maison des adolescents CASITA', a='Hôpital Avicenne, 125 rue de Stalingrad', cp='93000', v='Bobigny', lat=48.91274, lon=2.43578,
         tel='01 48 95 73 01', src='https://anmda.fr/fr/maison-des-adolescents-de-bobigny-casita'),
    dict(n='Maison des adolescents CASADO', a='2 bis rue Gibault', cp='93200', v='Saint-Denis', lat=48.93511, lon=2.35530,
         tel='01 48 13 16 43', src='https://anmda.fr/fr/maison-des-adolescents-casado-saint-denis'),
    dict(n='Maison des adolescents AMICA', a='4 allée Albert Camus', cp='93390', v='Clichy-sous-Bois', lat=48.90616, lon=2.55760,
         tel='01 43 88 23 64', w='http://www.mda93amica.fr/', h=['Du lundi au vendredi de 9 h 30 à 18 h'], pub='12 à 21 ans et leurs parents',
         src='https://anmda.fr/fr/maison-des-adolescents-de-clichy-sous-bois-amica'),
    dict(n='Maison de l’adolescent du Val-de-Marne', a='8 rue du Général Lacharrière', cp='94000', v='Créteil', lat=48.78770, lon=2.46421,
         tel='01 57 02 23 90', pub='11 à 25 ans et leurs proches', src='https://anmda.fr/fr/maison-de-ladolescent'),
    dict(n='Maison des adolescents Adobase (nord Seine-et-Marne)', a='7 rue du Docteur Nicole Mangin', cp='77400', v='Lagny-sur-Marne', lat=48.87321, lon=2.69809,
         tel='01 60 54 30 73', src='https://anmda.fr/fr/maison-des-adolescents-adobase-nord-seine-et-marne'),
    dict(n='Maison des adolescents ADO Sud 77', a='Maison des associations, 6 rue du Mont Ussy', cp='77300', v='Fontainebleau', lat=48.41463, lon=2.70203,
         tel='06 71 81 87 41', h=['Sur rendez-vous, secrétariat tous les jours de 9 h à 17 h', 'Autre permanence : Maison pour tous, 4 rue Jules Ferry, Montereau-Fault-Yonne'],
         src='https://anmda.fr/fr/maison-des-adolescents-ado-sud-77-seine-et-marne'),
]

def telecharge(fichier='annuaire-sp.json'):
    if os.path.exists(fichier):
        return json.load(open(fichier))
    where = ' or '.join(f'startswith(code_insee_commune,"{d}")' for d in DEPS)
    url = API + '?' + urllib.parse.urlencode(dict(where=where, select=CHAMPS))
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120))
    json.dump(d, open(fichier, 'w'), ensure_ascii=False)
    return d

def heure(h):
    h, m = h[:2].lstrip('0') or '0', h[3:5]
    return f'{h} h' + ('' if m == '00' else f' {m}')

JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

def horaires(p):
    """Horaires par jour (une ligne plus tardive remplace la précédente), puis jours consécutifs regroupés."""
    jour = {}
    for x in json.loads(p or '[]'):
        if x['nom_jour_debut'] not in JOURS or x['nom_jour_fin'] not in JOURS:
            continue
        cr = ', '.join(f"{heure(x[f'valeur_heure_debut_{i}'])}–{heure(x[f'valeur_heure_fin_{i}'])}" for i in (1, 2) if x.get(f'valeur_heure_debut_{i}'))
        for k in range(JOURS.index(x['nom_jour_debut']), JOURS.index(x['nom_jour_fin']) + 1):
            if cr:
                jour[k] = cr
    out, k = [], 0
    while k < 7:
        if k not in jour:
            k += 1; continue
        f = k
        while f + 1 < 7 and jour.get(f + 1) == jour[k]:
            f += 1
        j = JOURS[k] if f == k else f"{JOURS[k]} et {JOURS[f].lower()}" if f == k + 1 else f"{JOURS[k]} au {JOURS[f].lower()}"
        out.append(f'{j} : {jour[k]}')
        k = f + 1
    return out

def nom(t, n):
    v = n.split(' - ', 1)[1].strip().replace(' - ', ' – ') if ' - ' in n else ''
    if t == 'ml':
        return 'Mission locale' + (f' – {v}' if v else '')
    if t == 'cio':
        return 'CIO' + (f' – {v}' if v else '')
    return re.sub(r'\s+-\s+', ' – ', n)

lieux = []
for r in telecharge():
    types = [p['type_service_local'] for p in json.loads(r['pivot'] or '[]')]
    t = next((TYPES[x] for x in types if x in TYPES), None)
    if not t:
        continue
    a = (json.loads(r['adresse'] or '[]') or [{}])[0]
    if not a.get('latitude'):
        continue
    tel = (json.loads(r['telephone'] or '[]') or [{}])[0].get('valeur', '')
    w = (json.loads(r['site_internet'] or '[]') or [{}])[0].get('valeur', '')
    lieux.append(dict(t=t, n=nom(t, r['nom']), a=' '.join(x for x in (a.get('complement1'), a.get('numero_voie')) if x).strip(),
                      cp=a.get('code_postal', ''), v=a.get('nom_commune', ''), dep=DEPS[r['code_insee_commune'][:2]],
                      lat=round(float(a['latitude']), 5), lon=round(float(a['longitude']), 5), tel=tel, w=w,
                      h=horaires(r['plage_ouverture']), sp=r['url_service_public'], maj=r['date_modification'][:10]))
for m in MDA:
    lieux.append(dict(t='mda', dep=DEPS[m['cp'][:2]], **{k: v for k, v in m.items()}))

# Bibliothèques : ministère de la Culture, « Les bibliothèques des collectivités territoriales :
# adresses et données d'activité » (enquête annuelle, data.gouv.fr). Seules les bibliothèques
# municipales et intercommunales sont gardées : la loi du 21 décembre 2021 y garantit l'accès libre
# et la consultation sur place gratuite. Les points ouverts moins de 4 h par semaine sont écartés.
BIB = 'https://static.data.gouv.fr/resources/adresses-des-bibliotheques-publiques-2/20250827-130724/adresses-des-bibliotheques-publiques.json'

def nombre(x):
    try:
        return float(str(x).replace(',', '.'))
    except (TypeError, ValueError):
        return None

PETITS = {'de', 'du', 'des', 'la', 'le', 'les', 'et', 'sur', 'en', 'au', 'aux', 'sous', 'bis', 'ter'}

def casse(t):
    """Mots en capitales (souvent dans l'enquête) remis en casse normale ; le reste est gardé tel quel."""
    def mot(m):
        w = m.group(0)
        if not (w.isupper() and len(w) > 1):
            return w
        w = w.lower()
        return w if w in PETITS else w[0].upper() + w[1:]
    t = re.sub(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", mot, t or '')
    t = re.sub(r"\b([Dd]|[Ll])'(?=\w)", lambda m: m.group(1).lower() + "'", t)
    return re.sub(r'^\w', lambda m: m.group(0).upper(), re.sub(r'\s+', ' ', t).strip())

def nom_bib(n, ville):
    n = casse(n)
    n = re.sub(r'\bBiblioth[eè]que\b', 'Bibliothèque', n, flags=re.I)
    n = re.sub(r'\bM[eé]diath[eè]que\b', 'Médiathèque', n, flags=re.I)
    n = re.sub(r" (De|Des|Du|Et|La|Le|Les|Au|Aux) ", lambda m: ' ' + m.group(1).lower() + ' ', n)
    n = re.sub(r" D'", " d'", n).strip()
    n = re.sub(r'^(Bibliothèque|Médiathèque)( Municipale| Intercommunale| Territoriale| Centrale)\b', lambda m: m.group(1) + m.group(2).lower(), n)
    if not re.sub(r"(?i)biblioth[eè]que|m[eé]diath[eè]que|municipale|intercommunale|territoriale|centrale|de la ville|[\s\-–]", '', n):
        n = f'{n} – {ville}'
    return n

if not os.path.exists('bibliotheques.json'):
    urllib.request.urlretrieve(BIB, 'bibliotheques.json')
for r in json.load(open('bibliotheques.json')):
    d = str(r['code_departement'])
    if d not in DEPS or r['type_adresse'] != 'Bâtiment ouvert' or not r['latitude']:
        continue
    if r['statut'] not in ('Bibliothèque municipale', 'Bibliothèque intercommunale', 'Bibliothèque SIVOM'):
        continue
    if re.match(r'(?i)bibliobus', r['nom_de_l_etablissement'] or ''):
        continue
    amp = nombre(r['amplitude_horaire'])
    if amp is not None and amp < 4:
        continue
    tel = re.sub(r'\D', '', r['telephone'] or '')
    tel = ' '.join(tel[i:i + 2] for i in range(0, 10, 2)) if len(tel) == 10 else ''
    places, postes = nombre(r['nombre_de_places']), nombre(r['nb_postes_informatiques_publics'])
    lieux.append(dict(t='bib', n=nom_bib(r['nom_de_l_etablissement'], r['ville']),
                      a=casse(' '.join(x for x in (r['complement'], r['adresse']) if x).strip()), cp=str(r['cp']), v=r['ville'], dep=DEPS[d],
                      lat=round(float(r['latitude']), 5), lon=round(float(r['longitude']), 5), tel=tel, w=r['site_internet'] or '',
                      pl=int(places) if places else 0, po=int(postes) if postes else 0,
                      wifi=r['connexion_wi_fi'] == 'Oui', dim=r['ouverture_le_dimanche'] == 'Oui'))
lieux.sort(key=lambda x: (x['t'], x['v'], x['n']))

cols = json.load(open('colleges.json'))
out = dict(date='7 octobre 2026', lieux=lieux,
           colleges=[dict(n=c['nom_etablissement'], v=c['nom_commune'], lat=round(c['latitude'], 5), lon=round(c['longitude'], 5)) for c in cols if c.get('latitude')])
json.dump(out, open('aide.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import collections
print(os.path.getsize('aide.json'), collections.Counter(x['t'] for x in lieux), collections.Counter((x['t'], x['dep']) for x in lieux))
