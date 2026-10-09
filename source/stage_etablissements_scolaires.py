"""Lycées et collèges publics, lieux de PFMP pour la maintenance du bâtiment (domaines.py).

Source : annuaire de l'Éducation nationale (data.education.gouv.fr, fr-en-annuaire-education),
établissements ouverts, publics, de type « Lycée » ou « Collège », avec position et SIRET. Les
sections internes (SEP, SEGPA, sections d'enseignement…) et les doublons d'adresse sont écartés :
l'élève s'adresse à l'établissement principal. Les deux types sont recalculés en entier (aucun code
NAF) ; à relancer après une collecte nationale, qui ne les fabrique pas.

python3 source/stage_etablissements_scolaires.py --root /copie/carte-stages-donnees [--fichier export.json] [--write]
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.parse

from adresses import nettoie
from stage_collecte import ROOT
from stage_donnees import slug
from stage_nouveaux_codes import lire, publier

API = 'https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/exports/json?'
TYPES = {'Lycée': 'Lycées publics (maintenance)', 'Collège': 'Collèges publics (maintenance)'}
SECTION = re.compile(r"^(SECTION|SEGPA|SEP\b|SES\b|ANNEXE)", re.I)


def telecharger(path):
    q = dict(where="type_etablissement in ('Lycée','Collège') and statut_public_prive='Public' and etat='OUVERT'",
             select='identifiant_de_l_etablissement,nom_etablissement,type_etablissement,adresse_1,code_postal,'
                    'nom_commune,latitude,longitude,siren_siret,code_departement')
    subprocess.run(['curl', '-fsSL', '--max-time', '600', '--retry', '3', '-o', str(path), API + urllib.parse.urlencode(q)], check=True)
    rows = lire(path)
    if not isinstance(rows, list) or len(rows) < 9000:
        raise ValueError('Annuaire inattendu ou incomplet')
    return rows


def lignes(annuaire, allowed):
    out, ecartes, vus = defaultdict(list), Counter(), set()
    for a in sorted(annuaire, key=lambda a: (SECTION.search(a['nom_etablissement'] or '') is not None, a['identifiant_de_l_etablissement'])):
        nom = (a['nom_etablissement'] or '').strip()
        if SECTION.search(nom):
            ecartes['section_interne'] += 1
            continue
        if not a['siren_siret'] or not a['latitude']:
            ecartes['sans_siret_ou_position'] += 1
            continue
        dep = (a['code_departement'] or '').lstrip('0') if (a['code_departement'] or '').startswith('0') else (a['code_departement'] or '')
        dep = dep.zfill(2) if dep.isdigit() and len(dep) < 2 else dep
        if dep not in allowed:
            ecartes['hors_academies'] += 1
            continue
        cle = (round(a['latitude'], 4), round(a['longitude'], 4), a['type_etablissement'])
        if a['siren_siret'] in vus or cle in vus:
            ecartes['doublon'] += 1
            continue
        vus |= {a['siren_siret'], cle}
        adr, rep = nettoie(f"{a['adresse_1'] or ''} {a['code_postal'] or ''} {a['nom_commune'] or ''}")
        if adr:
            adr = adr[0].upper() + adr[1:]
        out[(dep, slug(TYPES[a['type_etablissement']]))].append(
            [nom, '', adr, round(float(a['latitude']), 5), round(float(a['longitude']), 5), 0, 0, a['siren_siret'], rep])
    return {k: sorted(v) for k, v in out.items()}, ecartes


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--fichier', type=Path, help='export déjà téléchargé (sinon téléchargé dans --cache)')
    p.add_argument('--cache', type=Path, default=Path.home()/'.cache'/'annuaire-education')
    p.add_argument('--rapport', default='etablissements-scolaires.json')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.write and subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() in ('main', 'master', ''):
        p.error('Écriture réservée à une branche de travail')
    if args.fichier:
        annuaire = lire(args.fichier)
    else:
        args.cache.mkdir(parents=True, exist_ok=True)
        annuaire = telecharger(args.cache/'publics.json')
    allowed = {d for a in lire(ROOT/'commun/academies.json') for d in a['deps']}
    fichiers, ecartes = lignes(annuaire, allowed)
    bilan = Counter()
    for (dep, k), rows in fichiers.items():
        bilan[k] += len(rows)
    print(json.dumps(dict(gardes=dict(bilan), ecartes=dict(ecartes)), ensure_ascii=False, indent=1))
    if args.write:
        publier(root, fichiers, args.rapport, dict(date=time.strftime('%Y-%m-%d'), source=API.split('/exports')[0],
                                                   gardes=dict(bilan), ecartes=dict(ecartes)))


if __name__ == '__main__':
    main()
