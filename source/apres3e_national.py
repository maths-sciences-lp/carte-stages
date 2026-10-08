"""Préparation nationale ; aucun accès à ces services depuis les pages élèves.

python3 source/apres3e.py --academies toutes --sources /dossier/des/sources
Le dossier contient le même 605340ddc19a9.csv que le mode historique et
pression_2025.json (Draio Créteil). Les exports ministériels sont mis en cache.
Un cache vide permet une nouvelle collecte ; les SHA-256 figurent au bilan.
"""
import argparse
import collections
import csv
import datetime
import difflib
import gzip
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import urllib.parse

from apres3e import T, construire

ROOT = Path(__file__).resolve().parents[1]
EDU = 'https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/'
ANN_URL = EDU + 'fr-en-annuaire-education/exports/json?' + urllib.parse.urlencode(dict(
    select='identifiant_de_l_etablissement,nom_etablissement,type_etablissement,nom_commune,latitude,longitude,code_departement,libelle_academie,hebergement,etat'))
IJ_URL = EDU + 'fr-en-inserjeunes-lycee_pro-formation-fine/exports/json?' + urllib.parse.urlencode(dict(
    where='annee="cumul 2023-2024"',
    select='annee,uai,type_diplome,libelle_formation,code_formation_mefstat11,taux_poursuite_etudes,taux_emploi_6_mois'))


def export(url, path):
    if not path.exists():
        temp = path.with_suffix('.part')
        subprocess.run(['curl', '--fail', '--location', '--retry', '3', '--silent', '--show-error',
                        '--max-time', '180', '-A', 'Mozilla/5.0', '-o', str(temp), url], check=True)
        data = json.loads(temp.read_text())
        if not isinstance(data, list) or not data:
            raise ValueError('Export vide ou inattendu : ' + url)
        temp.replace(path)
    return json.loads(path.read_text())


def coords(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        return math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180 and (lat, lon) != (0, 0)
    except (TypeError, ValueError):
        return False


def code_dep(value):
    return str(value).lstrip('0').zfill(2).upper()


def route_html(nom):
    return '''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Après le collège – ''' + html.escape(nom) + '''</title></head>
<body><p id="loading" role="status">Chargement des formations…</p>
<noscript>Active JavaScript pour choisir une formation et voir les lycées.</noscript>
<script src="../ouvrir.js"></script></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--academies', nargs='+', required=True, help='Slugs de commun/academies.json ou toutes')
    parser.add_argument('--sources', type=Path, default=Path.cwd(), help='CSV Onisep historique et pression_2025.json')
    parser.add_argument('--cache', type=Path, default=Path.home()/'.cache/carte-stages-apres3e')
    args = parser.parse_args()
    catalog = json.loads((ROOT/'commun/academies.json').read_text())
    selected = [a['slug'] for a in catalog] if args.academies == ['toutes'] else list(dict.fromkeys(args.academies))
    if set(selected) - {a['slug'] for a in catalog}:
        parser.error('Académie inconnue : ' + ', '.join(set(selected)-{a['slug'] for a in catalog}))
    source, cache = args.sources.resolve(), args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    csv_path, pression_path = source/'605340ddc19a9.csv', source/'pression_2025.json'
    if not csv_path.exists() or ('creteil' in selected and not pression_path.exists()):
        parser.error('Sources manquantes : fournir le CSV Onisep et, pour Créteil, pression_2025.json avec --sources')
    with csv_path.open(encoding='utf-8-sig') as f:
        rows = [r for r in csv.DictReader(f, delimiter=';') if r['FOR type'] in T]
    # Tous les types : une structure agricole/adaptée Onisep n'est pas toujours
    # classée « Lycée » dans l'annuaire. Le rapprochement reste l'UAI exact.
    ann = export(ANN_URL, cache/'annuaire-national-complet.json')
    export(IJ_URL, cache/'ij.json')
    by_uai = collections.defaultdict(list)
    for r in ann:
        by_uai[r['identifiant_de_l_etablissement']].append(r)
    # Un désaccord dans l'annuaire lui-même reste inconnu, jamais résolu au hasard.
    heb = {u: next(iter(v)) if len(v) == 1 else None for u, records in by_uai.items()
           for v in [{r['hebergement'] for r in records if r['etat'] == 'OUVERT'}]}
    # Le module historique lit ij.json à l'import. Ici il lit l'export national,
    # sans toucher au cache IDF ni aux consommateurs des autres outils.
    os.chdir(cache)
    from inserjeunes import IJ, split
    uncertain_ij = set()

    def cherche(uai, libelle, durees=()):
        t, n = split(libelle)
        candidates = []
        for tt, nn, r in IJ.get(uai, []):
            if tt != t:
                continue
            score = difflib.SequenceMatcher(None, nn, n).ratio()
            if score < .95:
                continue
            if nn != n and ('option' in nn or 'option' in n):
                oa = re.sub(r'^ [a-e] ', ' ', nn.split('option', 1)[1]) if 'option' in nn else ''
                ob = re.sub(r'^ [a-e] ', ' ', n.split('option', 1)[1]) if 'option' in n else ''
                if difflib.SequenceMatcher(None, oa, ob).ratio() < .95:
                    continue
            candidates.append((score, r))
        # Le 3e chiffre du code MEFSTAT11 est la durée du cycle (2311 : CAP en 1 an,
        # 2322 : CAP en 2 ans). Quand le lycée propose une seule de ces durées, elle
        # départage les chiffres ; sinon rien n'est choisi au hasard.
        ans = {m.group(1) for d in durees for m in [re.match(r'(\d) an', d)] if m}
        meme_duree = [(s, r) for s, r in candidates if r['code_formation_mefstat11'][2:3] in ans]
        if len(ans) == 1 and meme_duree:
            candidates = meme_duree
        # L'intitulé exact est prioritaire ; plusieurs formations/statistiques
        # encore possibles = aucun chiffre. Pas d'estimation ni de moyenne.
        if any(s == 1 for s, _ in candidates):
            candidates = [(s, r) for s, r in candidates if s == 1]
        unique = {(r['code_formation_mefstat11'], r['taux_poursuite_etudes'], r['taux_emploi_6_mois']) for _, r in candidates}
        if len(unique) > 1:
            uncertain_ij.add((uai, libelle))
        if len(unique) != 1:
            return None
        _, p, e = next(iter(unique))
        return dict(p=p, e=e)
    cherche.par_duree = True

    today = datetime.date.today().isoformat()
    outdir = ROOT/'apres-3e/data'
    outdir.mkdir(parents=True, exist_ok=True)
    summary, exclusions, missing_ann, urls_omises = [], [], set(), set()
    names = {re.sub(r"^Académie (?:de |d')", '', a['nom']) for a in catalog}
    outside = collections.Counter(r['ENS académie'] for r in rows if r['ENS académie'] not in names)
    for ac in catalog:
        if ac['slug'] not in selected:
            continue
        name = re.sub(r"^Académie (?:de |d')", '', ac['nom'])
        academy_rows = []
        for r in rows:
            if r['ENS académie'] != name:
                continue
            uai = r['ENS code UAI']
            reason = None
            if not coords(r['ENS latitude'], r['ENS longitude']):
                reason = 'Coordonnées absentes ou invalides'
            elif uai in by_uai and not any(x['etat'] == 'OUVERT' for x in by_uai[uai]):
                reason = 'Établissement non ouvert dans l’annuaire'
            elif r['ENS commune'] == 'Monaco':
                reason = 'Monaco rattaché à Nice dans Onisep : hors des départements du catalogue commun, cas à confirmer'
            if reason:
                exclusions.append(dict(ac=ac['slug'], uai=uai, n=r["Lieu d'enseignement (ENS) libellé"], formation=r['Formation (FOR) libellé'], motif=reason))
                continue
            if uai not in by_uai:
                missing_ann.add((ac['slug'], uai, r["Lieu d'enseignement (ENS) libellé"]))
            academy_rows.append(r)
        colleges = {}
        for r in ann:
            if (r['type_etablissement'] == 'Collège' and r['etat'] == 'OUVERT'
                    and code_dep(r['code_departement']) in ac['deps'] and coords(r['latitude'], r['longitude'])):
                # Un collège et son annexe peuvent partager le même UAI : garder les deux.
                colleges[(r['identifiant_de_l_etablissement'], r['nom_etablissement'], r['nom_commune'])] = r
        if not academy_rows or not colleges:
            raise ValueError('Académie sans formations ou collèges : ' + ac['slug'])
        pression = json.loads(pression_path.read_text()) if ac['slug'] == 'creteil' else []
        data = construire(academy_rows, heb, list(colleges.values()), cherche, pression, today)
        data['formations'] = [f for f in data['formations'] if f['e']]
        # La restriction filles est conservée au même titre que garçons.
        for f in data['formations']:
            for e in f['e']:
                for key in ['w', 'af']:
                    url = e[key].strip()
                    if url and (re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', url)
                                or urllib.parse.urlsplit(url if '://' in url else 'https://'+url).scheme not in ('http', 'https')):
                        urls_omises.add((ac['slug'], e['n'], key))
                        e[key] = ''
                if e.get('it') and e['h'].startswith('internat (femme)'):
                    e['ic'] = 'filles' + (' ; ' + e['ic'] if e.get('ic') else '')
        file = outdir/(ac['slug']+'.json')
        file.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        route = ROOT/'apres-3e'/ac['slug']/'index.html'
        route.parent.mkdir(parents=True, exist_ok=True)
        route.write_text(route_html(ac['nom']), encoding='utf-8')
        lycees = {e['o']: e for f in data['formations'] for e in f['e']}
        counts = collections.Counter(e.get('it', 'sans') for e in lycees.values())
        summary.append(dict(slug=ac['slug'], academie=name, formations=len(data['formations']),
                            offres=sum(len(f['e']) for f in data['formations']), lycees=len(lycees),
                            colleges=len(data['colleges']), internats=dict(counts),
                            inserjeunes=sum(bool(e['ij']) for f in data['formations'] for e in f['e']),
                            pression=sum('p' in e for f in data['formations'] for e in f['e']),
                            octets=file.stat().st_size, gzip_octets=len(gzip.compress(file.read_bytes(), mtime=0))))
        print(summary[-1], flush=True)
    national = ROOT/'apres-3e/france/index.html'
    national.parent.mkdir(parents=True, exist_ok=True)
    national.write_text(route_html('France'), encoding='utf-8')
    sources = [dict(nom=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                    date_fichier=datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds'))
               for p in [csv_path, cache/'annuaire-national-complet.json', cache/'ij.json'] + ([pression_path] if pression_path.exists() else [])]
    report = dict(date=today, academies=summary, sources=sources,
                  urls=dict(onisep='https://opendata.onisep.fr/data/605340ddc19a9/2-ideo-actions-de-formation-initiale-univers-lycee.htm', annuaire=ANN_URL, inserjeunes=IJ_URL,
                            pression='https://orientation.ac-creteil.fr/bilans-de-laffectation-de-lorientation/'),
                  academies_hors_catalogue=dict(outside), exclusions=exclusions,
                  lycees_absents_annuaire=[dict(ac=a, uai=u, nom=n) for a, u, n in sorted(missing_ann)],
                  urls_omises=[dict(ac=a, lycee=n, champ=k, motif='URL contenant un courriel ou protocole non web') for a, n, k in sorted(urls_omises)],
                  inserjeunes_ambigus=[dict(uai=u, formation=l) for u, l in sorted(uncertain_ij)])
    (outdir/'bilan.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if set(selected) == {a['slug'] for a in catalog}:
        # Lycées des académies voisines (mission 8.6) : recalculés avec toutes les académies.
        from apres3e_voisins import main as voisins
        voisins()
