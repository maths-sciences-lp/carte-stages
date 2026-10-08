"""Génère uniquement le dépôt national séparé, jamais data/ historique.

python3 source/build_domaines.py --national --sortie /copie/carte-stages-donnees
Collecte complète requise (101 départements) ; --academies permet un aperçu
local explicitement limité, qui ne peut pas être présenté comme national.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
import urllib.parse

from adresses import nettoie
from aides import ALIAS, ICON, FAMILLES, AUTRES, FAMILLES_SECTEURS
from domaines import COMMUNES_CJ, COMMUNES_NAF, DOMAINES, ECOLES_EXCLUES, ECOLES_NAF, FILTRES, MOTS_CLES, SANS_PERSONNEL, SOURCES_MOTS_CLES
from stage_collecte import atomic_json, ROOT, EFFECTIFS, CODES

EDU = 'https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/exports/json?'
ANN_URL = EDU + urllib.parse.urlencode(dict(where='etat="OUVERT" AND voie_professionnelle="1"',
    select='identifiant_de_l_etablissement,nom_etablissement,nom_commune,code_postal,code_departement,latitude,longitude,libelle_departement,libelle_nature,type_etablissement'))


def slug(s, limit=60):
    s = ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.category(c).startswith('M'))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:limit]


def catalogue_formations():
    """Catalogue national depuis les tables complètes, sans écrire l'index IDF."""
    domaines = [{'d':d, 'i':ICON.get(d, ''),
                 's':[{'n':s, 'k':slug(s)} for s in secs]}
                for d, secs in DOMAINES.items()]
    name2k = {s['n']:s['k'] for d in domaines for s in d['s']}
    if len(set(name2k.values())) != len(name2k):
        raise ValueError('Deux secteurs ont la même adresse')
    mapping = json.loads((ROOT/'source/formation_secteurs.json').read_text())
    # Certains intitulés ne se distinguent qu'après le 60e caractère (options).
    # Les nouvelles pages doivent pouvoir sélectionner chaque option séparément.
    occurrences = Counter(slug(n) for n in mapping)
    forms = []
    for n, secs in sorted(mapping.items(), key=lambda x:x[0].lower()):
        t = 'CAPa' if n.startswith('CAPa ') else 'CAP' if n.startswith('CAP ') else 'Bac pro'
        court = n[4:] if t == 'CAP' else n[5:] if t == 'CAPa' else n[8:]
        forms.append(dict(n=court[0].upper()+court[1:], t=t,
                          s=[name2k[x] for x in secs], a=ALIAS.get(n, ''),
                          k=slug(n, None) if occurrences[slug(n)] > 1 else slug(n)))
    for n, (a, lst) in FAMILLES.items():
        secs = ([name2k[x] for x in FAMILLES_SECTEURS[n]] if n in FAMILLES_SECTEURS
                else list(dict.fromkeys(name2k[x] for b in lst for x in mapping[b])))
        forms.append(dict(n=n, t='2nde pro', s=secs, a=a, k=slug('2nde '+n)))
    for n, (t, a, secs) in AUTRES.items():
        forms.append(dict(n=n, t=t, s=[name2k[x] for x in secs], a=a, k=slug(t+' '+n)))
    # Écoles : mêmes formations que les mairies, sauf géomètre et bâtiment.
    for f in forms:
        if 'mairies-administrations' in f['s'] and f['k'] not in ECOLES_EXCLUES:
            i = f['s'].index('mairies-administrations')
            f['s'] = f['s'][:i+1] + ['ecoles-maternelles-et-elementaires'] + f['s'][i+1:]
    if len({f['k'] for f in forms}) != len(forms):
        raise ValueError('Deux formations ont la même adresse')
    # Les libellés d'effectifs restent ceux de la page historique.
    eff = json.loads((ROOT/'data/index.json').read_text())['eff']
    if len(eff) != len(EFFECTIFS):
        raise ValueError('Tranches d’effectifs incompatibles')
    return dict(domaines=domaines, formations=forms, eff=eff)


def verifier_cache(cache):
    """Refuse notamment le cache antérieur aux ajouts France."""
    config = json.loads((cache/'configuration-collecte.json').read_text())
    fingerprint = hashlib.sha256('\n'.join(CODES).encode()).hexdigest()
    if config.get('codes_naf') != CODES or config.get('empreinte_naf') != fingerprint:
        raise ValueError('Le cache ne correspond pas aux codes NAF des tables actuelles')


def affiner(secteur, c, nj):
    """Catégories sans code propre, tirées de « Mairies, administrations » : écoles, communes."""
    if secteur != 'mairies-administrations':
        return secteur
    if c in ECOLES_NAF:
        return 'ecoles-maternelles-et-elementaires'
    if c in COMMUNES_NAF and str(nj or '').startswith(COMMUNES_CJ):
        return 'communes-et-intercommunalites'
    return secteur


def sans_personnel(secteur, c, nj, q):
    """Compte de collectivité ou ferme solaire (domaines.SANS_PERSONNEL) : secteur en adresse."""
    proprios = next((v.get(c, ()) for n, v in SANS_PERSONNEL.items() if slug(n) == secteur), ())
    return (('public' in proprios and str(nj or '').startswith('7'))
            or ('agricole' in proprios and str(q or '')[:2] in ('01', '02', '03')))


def preparer(rows):
    """Mêmes tables, filtres de noms et priorités que build_domaines.py."""
    sec_of = {}
    for secs in DOMAINES.values():
        for s, codes in secs.items():
            for c in codes:
                sec_of.setdefault(c, slug(s))
    filtres = {slug(k): re.compile(v) for k, v in FILTRES.items()}
    by, excluded = defaultdict(dict), Counter()
    for r in rows:
        if r['nj'] == '1000' or r['du'] != 'O' or r['de'] != 'O' or not r['la']:
            raise ValueError('Le cache contient un établissement interdit')
        if not isinstance(r['n'], str) or not r['n'].strip():
            excluded['sans_nom'] += 1
            continue
        k = sec_of.get(r['c']) or sec_of.get(r['q'])
        if k in filtres and not filtres[k].search((r['n'] + ' ' + (r['e'] or '')).upper()):
            k = sec_of.get(r['q']) if r['q'] != r['c'] else None
            if not k:
                excluded['hors_filtre_nom'] += 1
                continue
        if not k:
            excluded['activite_non_resolue'] += 1
            continue
        k = affiner(k, r['c'], r['nj'])
        if sans_personnel(k, r['c'], r['nj'], r['q']):
            excluded['sans_personnel'] += 1
            continue
        nom = re.sub(r'\s+', ' ', r['n']).strip()
        nom = re.sub(r'(\([^()]*\))(\s*\1)+', r'\1', nom)
        nom = re.sub(r'^(.+?) \(\1\)$', r'\1', nom)
        ens = r['e'] if r['e'] and r['e'].upper() not in nom.upper() else ''
        ens = ens.split(', ')[0] if ens else ''
        adr, rep = nettoie(r['ad'] or '')
        if adr:
            adr = adr[0].upper() + adr[1:]
        by[k][r['s']] = [nom, ens, adr, round(float(r['la']), 5), round(float(r['lo']), 5),
                         EFFECTIFS.index(r['t']) + 1 if r['t'] in EFFECTIFS else 0,
                         1 if r['r'] else 0, r['s'], rep]
    sources = {slug(s) for d, secs in DOMAINES.items() if d in SOURCES_MOTS_CLES for s in secs}
    for secteur, rx in MOTS_CLES.items():
        k, regex = slug(secteur), re.compile(rx)
        for sec, entries in list(by.items()):
            if sec == k or sec not in sources:
                continue
            for sir, row in entries.items():
                text = (row[0] + ' ' + row[1]).upper()
                if regex.search(text) and 'ENSEIGNEMENT' not in text:
                    by[k][sir] = row
    return {k: sorted(v.values()) for k, v in by.items()}, dict(excluded)


def export_annuaire(cache):
    path = cache/'lycees-annuaire.json'
    if not path.exists():
        temp = path.with_suffix('.part')
        subprocess.run(['curl', '-fsSL', '--max-time', '180', '--retry', '3', '-o', str(temp), ANN_URL], check=True)
        rows = json.loads(temp.read_text())
        if not isinstance(rows, list) or len(rows) < 1000:
            raise ValueError('Annuaire inattendu ou incomplet')
        temp.replace(path)
    return json.loads(path.read_text())


def fichier(path, value):
    atomic_json(path, value)
    raw = path.read_bytes()
    return dict(n=len(value), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    fingerprint = hashlib.sha256('\n'.join(CODES).encode()).hexdigest()
    parser.add_argument('--cache', type=Path,
                        default=Path.home()/('.cache/carte-stages-national-naf-'+fingerprint[:12]))
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--onisep', type=Path, required=True, help='Fichier Onisep 605340ddc19a9.csv pour le complément de lycées')
    parser.add_argument('--academies', nargs='+', default=['toutes'])
    args = parser.parse_args()
    out, cache = args.sortie.resolve(), args.cache.resolve()
    if out == ROOT or ROOT in out.parents or not (out/'.git').exists():
        parser.error('La sortie doit être la copie Git séparée du dépôt de données')
    try:
        verifier_cache(cache)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    acs = json.loads((ROOT/'commun/academies.json').read_text())
    if args.academies != ['toutes']:
        unknown = set(args.academies) - {a['slug'] for a in acs}
        if unknown:
            parser.error('Académie inconnue')
        acs = [a for a in acs if a['slug'] in args.academies]
    deps = sorted({d for a in acs for d in a['deps']})
    missing = [d for d in deps if not (cache/'departements'/f'{d}.json').exists()]
    if missing:
        parser.error('Collecte incomplète : ' + ', '.join(missing))
    index = catalogue_formations()
    sectors = [s['k'] for d in index['domaines'] for s in d['s']]
    schools, school_exclusions, names = defaultdict(list), [], {}
    for r in export_annuaire(cache):
        dep = str(r['code_departement']).lstrip('0').zfill(2)
        if dep not in deps:
            continue
        names[dep] = r['libelle_departement']
        try:
            lat, lon = float(r['latitude']), float(r['longitude'])
            if not -90 <= lat <= 90 or not -180 <= lon <= 180 or (lat, lon) == (0, 0):
                raise ValueError()
        except (ValueError, TypeError):
            school_exclusions.append(dict(uai=r['identifiant_de_l_etablissement'], dep=dep, raison='Sans position'))
            continue
        schools[dep].append(dict(u=r['identifiant_de_l_etablissement'], n=r['nom_etablissement'],
                           c=r['nom_commune'], p=r['code_postal'], la=round(lat, 6), lo=round(lon, 6)))
    bboxes = {d['code']: d['bbox'] for d in json.loads((ROOT/'commun/departements.json').read_text())}
    manifest, bilan, total = {}, [], Counter()
    for dep in deps:
        raw = json.loads((cache/'departements'/f'{dep}.json').read_text())
        groups, exclusions = preparer(raw['rows'])
        files = {}
        for sec in sectors:
            rows = groups.get(sec, [])
            files[sec] = fichier(out/'sirene'/dep/(sec+'.json'), rows)
            total[sec] += len(rows)
        lycees = sorted({l['u']: l for l in schools[dep]}.values(), key=lambda l: (l['c'], l['n']))
        lf = fichier(out/'lycees'/(dep+'.json'), lycees)
        manifest[dep] = dict(nom=names.get(dep, dep), bbox=bboxes[dep], secteurs=files, lycees=lf)
        unique = {r[7] for rows in groups.values() for r in rows}
        bilan.append(dict(**raw['bilan'], apres_classement=len(unique), exclusions_classement=exclusions,
                          lignes=sum(len(rows) for rows in groups.values()), lycees=len(lycees),
                          bytes=sum(v['bytes'] for v in files.values()) + lf['bytes']))
    for d in index['domaines']:
        for s in d['s']:
            s['c'] = total[s['k']]
    index['date'] = datetime.now(timezone.utc).date().isoformat()
    index['schema'] = 1
    index['academies'] = acs
    index['departements'] = manifest
    index['complet'] = len(deps) == 101
    index['version'] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(out/'catalogue.json', index)
    atomic_json(out/'bilan.json', dict(source_sirene='https://recherche-entreprises.api.gouv.fr/search',
                source_lycees=ANN_URL, departements=bilan, lycees_exclus=school_exclusions,
                tables_sha256={p: hashlib.sha256((ROOT/'source'/p).read_bytes()).hexdigest()
                               for p in ['domaines.py', 'formation_secteurs.json', 'aides.py']}))
    from stage_lycees import completer
    completer(out, args.onisep)
    (out/'.nojekyll').touch()
    print(f'{len(deps)} départements ; {sum(b["apres_classement"] for b in bilan)} établissements ; {sum(total.values())} lignes')


if __name__ == '__main__':
    main()
