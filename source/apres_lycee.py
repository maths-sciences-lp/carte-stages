"""« Après le lycée » pour toute l'académie de Créteil.

Diplômes de départ : CAP, CAP agricole, bac pro et BMA préparés en lycée (voie scolaire)
dans l'académie de Créteil (Onisep, Idéo-Actions de formation initiale, univers lycée).
Poursuites d'études : rubrique « Exemple(s) de formation(s) » de la fiche diplôme Onisep
(fiches/<id>.html), lieux en Île-de-France (univers lycée + enseignement supérieur).
Les 11 classes du lycée Eugène Hénaff gardent leurs listes relues à la main (suites.py).

Usage : python3 apres_lycee.py  ->  formations.json
"""
import csv, json, collections, html, re, os, sys
sys.path.insert(0, os.path.expanduser('~/Developer/carte-stages/source'))
from inserjeunes import cherche
from suites import SUITES
from aides import ALIAS
ALIAS = {k.lower(): v for k, v in ALIAS.items()}

HENAFF = '0932119Y'
TYPES = ('baccalauréat professionnel', 'CAP', 'CAP agricole', "brevet des métiers d'art")


def load(f):
    return [x for x in csv.DictReader(open(f, encoding='utf-8-sig'), delimiter=';')
            if x.get('ENS région', '') in ('Ile-de-France', 'Île-de-France')]


def cap1(s):
    return s[:1].upper() + s[1:]


def frais(s):
    s = (s or '').strip()
    if not s:
        return ''
    m = re.search(r'\((\d+) euros par an(.*?)\)', s)
    if m:
        n = f"{int(m.group(1)):,}".replace(',', ' ')
        return f"{n} € par an" + (f" ({m.group(2).strip(' ,')})" if m.group(2).strip(' ,') else '')
    return s


def exemples(forid):
    """Liste « Exemple(s) de formation(s) » de la fiche Onisep (None si fiche absente)."""
    p = f'fiches/{forid}.html'
    if not os.path.exists(p):
        return None
    s = open(p, encoding='utf-8').read()
    d = s.find('id="poursuites-etudes"')          # seulement la rubrique « Poursuites d'études »
    if d < 0:
        return []
    fin = s.find('class="border-brand', d)
    i = s.find('Exemple(s) de formation(s)', d, fin if fin > 0 else None)
    if i < 0:
        return []
    j = s.find('</ul>', i)
    return [html.unescape(re.sub(r'\s+', ' ', t)).strip()
            for t in re.findall(r'<a [^>]*>(.*?)</a>', s[i:j], flags=re.S)]


lycee = load('605340ddc19a9.csv')
rows = load('sup2.csv') + lycee
par_lib = collections.defaultdict(list)
for x in rows:
    par_lib[x['Formation (FOR) libellé'].lower()].append(x)

# Diplômes de départ et lycées qui les préparent (académie de Créteil)
dips, lycees = {}, {}
for x in lycee:
    if x.get('ENS académie') != 'Créteil' or x['FOR type'] not in TYPES:
        continue
    fid = x['FOR URL et ID Onisep'].rsplit('.', 1)[-1]
    d = dips.setdefault(fid, {'lib': cap1(x['Formation (FOR) libellé']), 'ly': set()})
    u = x['ENS code UAI']
    try:
        lat, lon = float(x['ENS latitude']), float(x['ENS longitude'])
    except ValueError:
        continue
    d['ly'].add(u)
    lycees.setdefault(u, {'n': x["Lieu d'enseignement (ENS) libellé"], 'v': x['ENS commune'],
                          'lat': round(lat, 5), 'lon': round(lon, 5)})

# Listes relues à la main pour les classes du lycée Hénaff
hen = {forid.split('.')[1]: (k, court, suites) for k, (court, lib, forid, suites) in SUITES.items()}

suites, manquantes = {}, []


def suite(nom):
    """Lieux en Île-de-France d'une poursuite d'études, mis en commun entre diplômes."""
    cle = nom.lower()
    if cle in suites:
        return cle if suites[cle]['e'] else None
    seen, f = {}, None
    for x in par_lib.get(cle, []):
        try:
            lat, lon = float(x['ENS latitude']), float(x['ENS longitude'])
        except ValueError:
            continue
        u = x['ENS code UAI'] or x["Lieu d'enseignement (ENS) libellé"]
        if u in seen:
            continue
        seen[u] = dict(n=x["Lieu d'enseignement (ENS) libellé"], st=x['ENS statut'], a=x['ENS adresse'],
                       cp=x['ENS code postal'], v=x['ENS commune'], lat=round(lat, 5), lon=round(lon, 5),
                       w=x['ENS site web'], o=x['ENS URL et ID Onisep'], h=x['ENS hébergement'],
                       af=x['AF page web'], c=frais(x['AF coût scolarité']),
                       ij=cherche(x['ENS code UAI'], x['Formation (FOR) libellé']))
        f = f or dict(t=x['FOR type'], o=x['FOR URL et ID Onisep'], d=x['AF durée cycle standard'])
    suites[cle] = dict(n=cap1(nom), **(f or {}), e=list(seen.values()))
    return cle if seen else None


out_dips, sans_fiche = {}, []
for fid, d in sorted(dips.items(), key=lambda kv: kv[1]['lib']):
    if fid in hen:
        liste = hen[fid][2]
    else:
        liste = exemples(fid)
        if liste is None:
            sans_fiche.append(fid)
            liste = []
    s, ailleurs = [], []
    for nom in liste:
        k = suite(nom)
        (s if k else ailleurs).append(k or cap1(nom))
    out_dips[fid] = {'lib': d['lib'], 'al': ALIAS.get(d['lib'].lower(), ''),
                     'o': 'https://www.onisep.fr/http/redirection/formation/slug/FOR.' + fid,
                     's': s, 'a': ailleurs, 'ly': sorted(d['ly'])}

classes = [{'k': k, 'n': court, 'd': forid.split('.')[1]} for k, (court, lib, forid, _) in SUITES.items()]
utiles = {u for d in out_dips.values() for u in d['ly']}
out = {'date': 'octobre 2026', 'henaff': HENAFF, 'classes': classes,
       'lycees': {u: v for u, v in lycees.items() if u in utiles},
       'dip': out_dips, 'suites': {k: v for k, v in suites.items() if v['e']}}
json.dump(out, open('formations.json', 'w'), ensure_ascii=False, separators=(',', ':'))

print('diplômes', len(out_dips), '· lycées', len(out['lycees']), '· poursuites avec lieux', len(out['suites']),
      '· lieux', sum(len(v['e']) for v in out['suites'].values()), '·', os.path.getsize('formations.json') // 1024, 'ko')
print('sans fiche téléchargée :', sans_fiche)
print('sans aucune poursuite :', [out_dips[k]['lib'] for k in out_dips if not out_dips[k]['s'] and not out_dips[k]['a']])
print('poursuites seulement ailleurs :', [out_dips[k]['lib'] for k in out_dips if not out_dips[k]['s'] and out_dips[k]['a']])
