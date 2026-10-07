"""Prépare les données de « Qui peut m'aider ? ».
Sans paramètre : mode historique, aide.json dans le dossier courant.
Avec --academies : sorties nationales, sans écrire aide/aide.json. Voir README.md.
"""
import argparse
import collections
import datetime
import html
import json
import math
import os
from pathlib import Path
import re
import time
import subprocess
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'aide' / 'data'
API = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/exports/json'
CHAMPS = 'id,nom,pivot,adresse,telephone,site_internet,plage_ouverture,code_insee_commune,url_service_public,date_modification'
BIB = 'https://static.data.gouv.fr/resources/adresses-des-bibliotheques-publiques-2/20250827-130724/adresses-des-bibliotheques-publiques.json'
EDU = 'https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/exports/json'
ANMDA = 'https://anmda.fr/fr/annuaire-mda'
CONTOURS = 'https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-100m.geojson'
ACADEMIES_SOURCE = 'https://www.education.gouv.fr/les-regions-academiques-academies-et-services-departementaux-de-l-education-nationale-6557'
# Catalogue partagé avec les futures versions nationales des autres outils.
CATALOGUE = json.loads((ROOT / 'commun' / 'academies.json').read_text(encoding='utf-8'))
def nom_court(ac):
    return re.sub(r"^Académie (?:de |d')", '', ac['nom'])
SLUGS = {ac['slug']: nom_court(ac) for ac in CATALOGUE}
ACAD = {d: nom_court(ac) for ac in CATALOGUE for d in ac['deps']}
if len(ACAD) != sum(len(ac['deps']) for ac in CATALOGUE):
    raise ValueError('Département partagé entre académies : vérifier la source officielle')
TYPES = {'cio': 'cio', 'mission_locale': 'ml', 'cij': 'ij'}
JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
PETITS = {'de', 'du', 'des', 'la', 'le', 'les', 'et', 'sur', 'en', 'au', 'aux', 'sous', 'bis', 'ter'}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    tmp.replace(path)


def download(url, path, delay=0):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        if delay:
            time.sleep(delay)
        tmp = path.with_suffix(path.suffix + '.tmp')
        # curl utilise le magasin de certificats du système (pas de désactivation TLS).
        subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                        '--retry', '3', '--retry-delay', '3', '--max-time', '180',
                        '--user-agent', 'Mozilla/5.0', '--output', str(tmp), url], check=True)
        tmp.replace(path)
    return path.read_bytes()


def get_json(url, path):
    return json.loads(download(url, path))


def dep_code(code):
    code = str(code or '')
    return code[:3] if code.startswith(('97', '98')) else code[:2]


def nested(value):
    return json.loads(value or '[]') if isinstance(value, str) else value or []


def coords(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        if lat == lon == 0:
            return None
        return dict(lat=round(lat, 5), lon=round(lon, 5))
    except (ValueError, TypeError):
        return None


def safe_url(url):
    if not url or '@' in url or re.search(r'(?i)(mailto:|javascript:)', url):
        return ''
    return url if re.match(r'^https?://', url) else ''


def telephone(value):
    # Certaines fiches mettent deux numéros dans le même champ : garder le premier,
    # jamais concaténer 20 chiffres en un numéro impossible à appeler.
    value = value or ''
    match = re.search(r'(?<!\d)(?:\+33\s*(?:\(0\)\s*)?[1-9]|0[1-9])(?:[\s.\u00a0-]*\d){8}(?!\d)', value)
    digits = re.sub(r'[^\d+]', '', match.group(0) if match else value)
    if len(digits) == 10 and digits.startswith('0'):
        return ' '.join(digits[i:i+2] for i in range(0, 10, 2))
    return digits if re.fullmatch(r'\+\d{10,14}', digits) else ''


def heure(h):
    h, m = h[:2].lstrip('0') or '0', h[3:5]
    return f'{h} h' + ('' if m == '00' else f' {m}')


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


def nombre(x):
    try:
        return float(str(x).replace(',', '.'))
    except (TypeError, ValueError):
        return None


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


def collect_mda(cache):
    """Annuaire paginé + fiches, 2,5 s entre téléchargements ; cache reprenable.
    Seuls les champs publics de la structure sont extraits, jamais les contacts nominatifs.
    """
    from bs4 import BeautifulSoup
    first = download(ANMDA, cache / 'annuaire.html', 2.5)
    soup = BeautifulSoup(first, 'html.parser')
    pages = [int(x) for a in soup.select('.pagination a') for x in re.findall(r'[?&]page=(\d+)', a.get('href', ''))]
    urls = set()
    for p in range(max(pages, default=0) + 1):
        s = soup if p == 0 else BeautifulSoup(download(ANMDA + '?page=' + str(p), cache / f'annuaire-{p}.html', 2.5), 'html.parser')
        for a in s.select('.views-row h5 a, .views-field-field-nom-de-la-structure a'):
            if a.get('href', '').startswith('/fr/'):
                urls.add('https://anmda.fr' + a['href'])
    if not urls:
        raise ValueError('Annuaire ANMDA vide ou structure HTML modifiée ; aucun relevé remplacé')
    print(f'ANMDA : {len(urls)} fiches', flush=True)
    entries, review = [], []
    for i, url in enumerate(sorted(urls)):
        path = cache / 'mda' / (url.rsplit('/', 1)[-1] + '.html')
        page = BeautifulSoup(download(url, path, 2.5), 'html.parser')
        article = page.select_one('article.profile')
        if not article:
            raise ValueError('Fiche ANMDA non reconnue : ' + url)
        def field(selector):
            e = article.select_one(selector)
            return re.sub(r'\s+', ' ', e.get_text(' ', strip=True)) if e else ''
        name = field('.field--name-field-nom-de-la-structure')
        opening = article.select_one('.field--name-field-heure-ouverture .field__item')
        h = opening.get_text('\n', strip=True).splitlines() if opening else []
        h = [line for line in h if not re.search(r'@|https?://', line)]
        loc = article.select_one('[data-lat][data-lng]')
        c = coords(loc['data-lat'], loc['data-lng']) if loc else None
        r = dict(n=name, a=' '.join(field('.'+x) for x in ['address-line1','address-line2'] if field('.'+x)),
                 cp=field('.postal-code'), v=casse(field('.locality')),
                 tel=telephone(field('.field--name-field-telephone')), h=h, src=url)
        web = article.select_one('.field--name-field-lien-s-internet a')
        if web and safe_url(web.get('href')):
            r['w'] = web['href']
        if c:
            r.update(c)
        # Ne publie aucune description libre (contacts personnels possibles).
        # Les indices d'atelier et données incomplètes sont tracés pour vérification.
        description = field('.field--name-field-description .field__item')
        if re.search(r'atelier', name+' '+' '.join(h)+' '+description, re.I):
            review.append(dict(src=url, n=name, motif='mention atelier à examiner', extrait=description, h=h))
        entries.append(r)
        if i % 20 == 0:
            print(f'ANMDA {i+1}/{len(urls)}', flush=True)
    write_json(cache / 'mda-review.json', review)
    write_json(OUT / 'mda-france.json', dict(date=datetime.date.today().isoformat(), fiches=entries))
    return entries


def departement_point(lat, lon, features):
    def ring(points):
        inside = False
        for i in range(len(points)):
            xi, yi = points[i]
            xj, yj = points[i-1]
            if (yi > lat) != (yj > lat) and lon < (xj-xi)*(lat-yi)/(yj-yi)+xi:
                inside = not inside
        return inside
    matches = []
    for f in features:
        g = f['geometry']
        polygons = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        if any(ring(p[0]) and not any(ring(h) for h in p[1:]) for p in polygons):
            matches.append(f['properties']['code'])
    return matches[0] if len(matches) == 1 else None


def route_html(ac):
    return ('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Qui peut m’aider ? – {html.escape(ac)}</title></head>'
            '<body><p id="loading" role="status">Chargement…</p>'
            '<noscript>Active JavaScript pour chercher un lieu. Pour parler à quelqu’un : '
            '<a href="tel:0800235236">Fil Santé Jeunes, 0 800 235 236</a>.</noscript>'
            '<script src="../ouvrir.js"></script></body></html>\n')


def build(args):
    cache = args.cache.expanduser()
    selected = list(SLUGS) if args.academies == ['toutes'] else (args.academies or [])
    if any(s not in SLUGS for s in selected):
        raise ValueError('Académie inconnue. Utiliser : ' + ', '.join(SLUGS))
    if args.mda_only:
        collect_mda(cache)
        return
    departments = get_json('https://geo.api.gouv.fr/departements', cache / 'departements.json')
    names = {d['code']: d['nom'] for d in departments}
    contours = get_json(CONTOURS, cache / 'contours-100m.json')
    features = [f for f in contours['features'] if f['properties']['code'] in ACAD]
    assert len(features) == 101
    bounds = []
    for f in features:
        g = f['geometry']
        polygons = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        points = [p for poly in polygons for ring in poly for p in ring]
        xs, ys = zip(*points)
        bounds.append(dict(code=f['properties']['code'], bbox=[min(xs), min(ys), max(xs), max(ys)]))
        write_json(ROOT / 'commun' / 'contours' / (f['properties']['code'] + '.json'), f)
    write_json(ROOT / 'commun' / 'departements.json', bounds)
    places = []
    excluded = []
    def add(r, d):
        email = r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'
        had_email = bool(re.search(email, r.get('a', '')))
        for key in ('n', 'a', 'v'):
            r[key] = re.sub(email, '', r.get(key, '')).strip()
        r['h'] = [re.sub(r' ([?!:;])', r' \1', re.sub(email, '', line).strip()) for line in r.get('h', [])]
        if had_email and (not r['a'] or re.fullmatch(r'\d+\s+(?:rue|avenue|route|place)', r['a'], re.I)):
            excluded.append(dict(n=r['n'], src=r.get('src', r.get('sp', BIB)), motif='Adresse absente ou incomplète après retrait d’un courriel dans le champ adresse'))
            return
        if d not in ACAD:
            excluded.append(dict(n=r['n'], src=r.get('src', r.get('sp','')), motif='Hors des 30 académies ou département absent', code=d))
            return
        r.update(dep=names[d], ac=ACAD[d])
        places.append(r)
    where = ' or '.join(f'pivot LIKE "%{t}%"' for t in TYPES)
    # Select explicite : affectation_personne et courriel ne sont jamais téléchargés.
    sp_url = API + '?' + urllib.parse.urlencode(dict(select=CHAMPS, where=where))
    services = get_json(sp_url, cache / 'annuaire-national.json')
    for r in services:
        ts = [p['type_service_local'] for p in nested(r['pivot'])]
        t = next((TYPES[x] for x in ts if x in TYPES), None)
        if not t:
            continue
        addresses = nested(r['adresse'])
        a = next((a for a in addresses if a.get('type_adresse') == 'Adresse'), addresses[0] if addresses else {})
        c = coords(a.get('latitude'), a.get('longitude'))
        if not c:
            excluded.append(dict(n=r['nom'], src=r['url_service_public'], motif='Coordonnées absentes ou invalides'))
            continue
        tel = (nested(r['telephone']) or [{}])[0].get('valeur','')
        web = (nested(r['site_internet']) or [{}])[0].get('valeur','')
        add(dict(t=t, n=nom(t,r['nom']), a=' '.join(x for x in [a.get('complement1'),a.get('complement2'),a.get('numero_voie')] if x),
                 cp=a.get('code_postal',''),v=a.get('nom_commune',''), **c, tel=telephone(tel), w=safe_url(web),
                 h=horaires(r['plage_ouverture']), sp=r['url_service_public'], maj=(r['date_modification'] or '')[:10]), dep_code(r['code_insee_commune']))
    for r in get_json(BIB, cache / 'bibliotheques.json'):
        d = str(r['code_departement']).zfill(2)
        c = coords(r['latitude'],r['longitude'])
        if d not in ACAD or r['type_adresse'] != 'Bâtiment ouvert' or not c:
            continue
        if r['statut'] not in ('Bibliothèque municipale','Bibliothèque intercommunale','Bibliothèque SIVOM'):
            continue
        if re.match(r'(?i)bibliobus', r['nom_de_l_etablissement'] or ''):
            continue
        amp = nombre(r['amplitude_horaire'])
        if amp is not None and amp < 4:
            continue
        seats, pcs = nombre(r['nombre_de_places']), nombre(r['nb_postes_informatiques_publics'])
        add(dict(t='bib', n=nom_bib(r['nom_de_l_etablissement'],casse(r['ville'])),
                 a=casse(' '.join(x for x in [r['complement'],r['adresse']] if x)), cp=str(r['cp']).zfill(5), v=casse(r['ville']),
                 **c, tel=telephone(r['telephone']),w=safe_url(r['site_internet'] or ''),
                 pl=int(seats) if seats else 0,po=int(pcs) if pcs else 0,wifi=r['connexion_wi_fi']=='Oui',dim=r['ouverture_le_dimanche']=='Oui'),d)
    mda_path = OUT / 'mda-france.json'
    mda = collect_mda(cache) if args.refresh_mda or not mda_path.exists() else json.loads(mda_path.read_text())['fiches']
    decisions_path = OUT / 'mda-exclusions.json'
    decisions = json.loads(decisions_path.read_text()) if decisions_path.exists() else []
    omit = {r['src']: r['motif'] for r in decisions}
    for m in mda:
        if m['src'] in omit or not coords(m.get('lat'),m.get('lon')) or not m['a'] or not m['cp']:
            excluded.append(dict(n=m['n'],src=m['src'],motif=omit.get(m['src'],'Adresse ou coordonnées absentes')))
            continue
        d = dep_code(m['cp'])
        if m['cp'] in ('97133', '97150'):
            excluded.append(dict(n=m['n'],src=m['src'],motif='Saint-Barthélemy ou Saint-Martin : rattachement à confirmer, ne pas assimiler le code postal au département 971'))
            continue
        if d == '20':
            # Le code postal seul ne distingue pas les deux départements corses.
            url = 'https://geo.api.gouv.fr/communes?' + urllib.parse.urlencode(dict(codePostal=m['cp'], fields='code,codeDepartement,nom'))
            communes = get_json(url, cache / ('communes-' + m['cp'] + '.json'))
            deps = {r['codeDepartement'] for r in communes}
            d = next(iter(deps)) if len(deps) == 1 else None
        add(dict(t='mda',**m), d)
    edu_url = EDU + '?' + urllib.parse.urlencode(dict(where='type_etablissement="Collège" and etat="OUVERT"',select='identifiant_de_l_etablissement,nom_etablissement,nom_commune,latitude,longitude,code_departement,libelle_academie'))
    raw_colleges = get_json(edu_url, cache / 'colleges-national.json')
    # L'annuaire peut donner plusieurs lignes pour le même UAI.
    colleges = list({r['identifiant_de_l_etablissement']: r for r in raw_colleges
                     if coords(r['latitude'], r['longitude'])}.values())
    hors_deps = collections.Counter(str(r['code_departement']) for r in colleges if str(r['code_departement']).lstrip('0').zfill(2) not in ACAD)
    today = datetime.date.today().isoformat()
    summary = []
    for s in selected:
        ac = SLUGS[s]
        ls = sorted([r for r in places if r['ac']==ac],key=lambda x:(x['t'],x['v'],x['n']))
        cs = [dict(n=r['nom_etablissement'],v=' '.join(r['nom_commune'].split()),**coords(r['latitude'],r['longitude']),ac=ac)
              for r in colleges if ACAD.get(str(r['code_departement']).lstrip('0').zfill(2))==ac and coords(r['latitude'],r['longitude'])]
        if not cs:
            raise ValueError('Aucun collège : '+ac)
        path = OUT / (s + '.json')
        write_json(path, dict(date=today, lieux=ls, colleges=cs))
        route = ROOT / 'aide' / s / 'index.html'
        route.parent.mkdir(parents=True, exist_ok=True)
        route.write_text(route_html(ac), encoding='utf-8')
        summary.append(dict(academie=ac,slug=s,types=dict(collections.Counter(r['t'] for r in ls)),colleges=len(cs),octets=path.stat().st_size))
    write_json(OUT / 'bilan.json', dict(date=today, academies=summary, exclusions=excluded, colleges_hors_perimetre=dict(hors_deps),
               sources=dict(service_public=sp_url,bibliotheques=BIB,colleges=edu_url,mda=ANMDA,academies=ACADEMIES_SOURCE,contours=CONTOURS)))
    for row in summary:
        print(row)


def generation_idf():
    """Mode historique, mêmes règles et ordre de sérialisation ; sortie dans le cwd.
    Le cache historique est indispensable pour une reproduction à l'octet près.
    Ne jamais le remplacer par les résultats d'une collecte nationale plus récente.
    """
    requis = ['annuaire-sp.json', 'bibliotheques.json']
    requis.append('colleges_idf.json' if Path('colleges_idf.json').exists() else 'colleges.json')
    manquants = [p for p in requis if not Path(p).exists()]
    if manquants:
        raise FileNotFoundError('Sources historiques manquantes : ' + ', '.join(manquants))
    API = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/exports/json'

    CHAMPS = 'id,nom,pivot,adresse,telephone,site_internet,plage_ouverture,code_insee_commune,url_service_public,date_modification'

    TYPES = {'cio': 'cio', 'mission_locale': 'ml', 'cij': 'ij'}

    DEPS = {'77': 'Seine-et-Marne', '93': 'Seine-Saint-Denis', '94': 'Val-de-Marne', '75': 'Paris', '78': 'Yvelines',
            '91': 'Essonne', '92': 'Hauts-de-Seine', '95': 'Val-d’Oise'}

    ACAD = {'77': 'Créteil', '93': 'Créteil', '94': 'Créteil', '75': 'Paris', '78': 'Versailles', '91': 'Versailles', '92': 'Versailles', '95': 'Versailles'}

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

    JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

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

    MDA += json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mda_idf.json')))

    for m in MDA:
        lieux.append(dict(t='mda', dep=DEPS[m['cp'][:2]], **{k: v for k, v in m.items()}))

    BIB = 'https://static.data.gouv.fr/resources/adresses-des-bibliotheques-publiques-2/20250827-130724/adresses-des-bibliotheques-publiques.json'

    PETITS = {'de', 'du', 'des', 'la', 'le', 'les', 'et', 'sur', 'en', 'au', 'aux', 'sous', 'bis', 'ter'}

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

    _dep2code = {v: k for k, v in DEPS.items()}

    for l in lieux:
        l['ac'] = ACAD[_dep2code[l['dep']]]

    lieux.sort(key=lambda x: (x['t'], x['v'], x['n']))

    cols = json.load(open('colleges_idf.json' if os.path.exists('colleges_idf.json') else 'colleges.json'))

    out = dict(date='7 octobre 2026', lieux=lieux,
               colleges=[dict(n=c['nom_etablissement'], v=' '.join(c['nom_commune'].split()), lat=round(c['latitude'], 5), lon=round(c['longitude'], 5)) for c in cols if c.get('latitude')])

    json.dump(out, open('aide.json', 'w'), ensure_ascii=False, separators=(',', ':'))

    print(os.path.getsize('aide.json'), collections.Counter(x['t'] for x in lieux), collections.Counter((x['t'], x['dep']) for x in lieux))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--academies', nargs='+', default=None, help='Slugs ou toutes ; Île-de-France par défaut')
    parser.add_argument('--cache', type=Path, default=Path.home()/'.cache'/'carte-stages-aide')
    parser.add_argument('--refresh-mda', action='store_true')
    parser.add_argument('--mda-only', action='store_true')
    args = parser.parse_args()
    if args.mda_only or args.academies:
        build(args)
    else:
        generation_idf()

if __name__ == '__main__':
    main()
