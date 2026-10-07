"""Chiffres Parcoursup des BTS et BTSA d'« Après le lycée » (formation/parcoursup.json).

Source : jeu « fr-esr-parcoursup » de data.enseignementsup-recherche.gouv.fr (session la plus
récente publiée, Licence Ouverte), lignes d'Île-de-France, filière BTS.
Les lieux de formations.json n'ont pas de code UAI : un lieu Onisep est relié à une ligne
Parcoursup quand le BTS est le même (même spécialité, même option ou 1re année commune)
et que la formation est sur le même site (moins de 100 m), ou à moins de 2 km avec un nom
d'établissement proche.

Usage historique : python3 source/parcoursup.py  ->  formation/parcoursup.json
National : python3 source/parcoursup.py --academies toutes --cache CACHE
Les noms différents exigent une décision documentée dans formation_parcoursup_revues.json.
Clé : « <n° Onisep formation>|<n° Onisep établissement> » (fin des liens f.o et e.o).
Valeurs : pl places, c candidats, a admis, bp admis venant d'un bac pro, g n° de la fiche Parcoursup
(g_ta_cod),
co = 1 si les chiffres portent sur la 1re année commune à toutes les options.
"""
import json, os, re, unicodedata, difflib, math, urllib.request, urllib.parse

ICI = os.path.dirname(os.path.abspath(__file__))
FORM = os.path.join(ICI, '..', 'formation', 'formations.json')
SORTIE = os.path.join(ICI, '..', 'formation', 'parcoursup.json')
API = 'https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/'
IDF = ('75', '77', '78', '91', '92', '93', '94', '95')


def get(url, **q):
    if q:
        url += '?' + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={'User-Agent': 'carte-stages (maths-sciences-lp)'})
    return json.load(urllib.request.urlopen(req, timeout=120))


def jeu_recent():
    """Le jeu courant porte l'identifiant sans année ; on lit sa session dans les données."""
    r = get(API + 'fr-esr-parcoursup/records', group_by='session', limit=20)
    return 'fr-esr-parcoursup', max(str(x['session']) for x in r['results'] if x['session'])


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]', ' ', s)).strip()


def decoupe(s):
    """« … option A : xxx » -> (tronc, 'a') ; 1re année commune -> (tronc, '*')."""
    n = norm(s)
    n = re.sub(r'^btsa? ', '', n)
    if re.search(r'1ere annee commune|premiere annee commune', n):
        return re.sub(r' ?(1ere|premiere) annee commune.*', '', n).strip(), '*'
    m = re.search(r' option ([a-e])\b', n)
    if m:
        return n[:m.start()].strip(), m.group(1)
    m = re.search(r' option (.*)$', n)
    if m:
        return n[:m.start()].strip(), m.group(1)
    return n, ''


def meme_bts(onisep, psup):
    (ta, oa), (tb, ob) = decoupe(onisep), decoupe(psup)
    if difflib.SequenceMatcher(None, ta, tb).ratio() < 0.9:
        return False
    if ob in ('*', ''):          # 1re année commune, ou option non précisée par Parcoursup
        return True
    if oa == ob:
        return True
    return len(oa) > 1 and len(ob) > 1 and difflib.SequenceMatcher(None, oa, ob).ratio() >= 0.9


def km(a, b, c, d):
    t = math.pi / 180
    x, y = (c - a) * t, (d - b) * t
    h = math.sin(x / 2) ** 2 + math.cos(a * t) * math.cos(c * t) * math.sin(y / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


VIDES = set("""lycee polyvalent general generale technologique professionnel prive privee de la le les des du
et l d en ecole campus site institut institution groupe paris superieure superieur lgt lp pole sts ensemble
business school metiers agricole ex enseignement regional etablissement adapte secteur""".split())
PRENOMS = set('jean marie pierre saint sainte louis paul andre henri charles francois notre dame st'.split())


def nom_proche(a, b, d):
    """Noms d'établissement qui partagent au moins la moitié de leurs mots distinctifs, dont un
    qui n'est pas un prénom courant (Jean Rose ≠ Jean Lurçat ; Saint-Pierre = Saint Pierre).
    À moins de 500 m, un seul mot distinctif commun suffit (École du Breuil)."""
    A, B = set(norm(a).split()) - VIDES, set(norm(b).split()) - VIDES
    commun = A & B
    if not commun:
        return False
    if d < 0.5 and commun - PRENOMS:
        return True
    return bool(commun - PRENOMS or commun in (A, B)) and len(commun) / min(len(A), len(B)) >= 0.5


def historique():
    jeu, session = jeu_recent()
    lignes = get(API + jeu + '/exports/json',
                 where='fili="BTS" and dep in (%s)' % ','.join('"%s"' % d for d in IDF))
    lignes = [r for r in lignes if r.get('g_olocalisation_des_formations')]
    print('Parcoursup', session, ':', len(lignes), 'formations BTS en Île-de-France')

    D = json.load(open(FORM, encoding='utf-8'))
    out, total, relies = {}, 0, 0
    for f in D['suites'].values():
        if not f['n'].startswith('BTS'):
            continue
        cands = [r for r in lignes if meme_bts(f['n'], r['fil_lib_voe_acc'])]
        for e in f['e']:
            total += 1
            best = None
            for r in cands:
                g = r['g_olocalisation_des_formations']
                d = km(e['lat'], e['lon'], g['lat'], g['lon'])
                if d < 0.1 or (d < 2 and nom_proche(e['n'], r['g_ea_lib_vx'], d)):
                    if best is None or d < best[0]:
                        best = (d, r)
            if not best:
                continue
            r = best[1]
            relies += 1
            cle = f['o'].rsplit('.', 1)[-1] + '|' + e['o'].rsplit('.', 1)[-1]
            out[cle] = dict(pl=r['capa_fin'], c=r['voe_tot'], a=r['acc_tot'], bp=r['acc_bp'],
                            g=None)
            m = re.search(r'g_ta_cod=(\d+)', r['lien_form_psup'] or '')
            if m:
                out[cle]['g'] = int(m.group(1))
            else:
                del out[cle]['g']
            if decoupe(f['n'])[1] and decoupe(r['fil_lib_voe_acc'])[1] in ('*', ''):
                out[cle]['co'] = 1      # chiffres de la 1re année, commune à toutes les options

    json.dump({'session': session, 'f': out}, open(SORTIE, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('lieux de BTS', total, '· reliés à Parcoursup', relies, '·', os.path.getsize(SORTIE) // 1024, 'ko')

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        historique()
    else:
        from formation_parcoursup import main
        main()
