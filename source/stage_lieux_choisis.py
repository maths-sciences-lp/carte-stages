"""Lieux choisis à la main (lieux_choisis.json) : ateliers vérifiés un par un, hors codes NAF.

Chaque SIRET est relu dans l'API Recherche d'entreprises (établissement actif, adresse et
position) ; un SIRET fermé ou introuvable arrête le script. Les types sont recalculés en entier ;
à relancer après une collecte nationale, qui ne les fabrique pas.

python3 source/stage_lieux_choisis.py --root /copie/carte-stages-donnees [--write]
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import time
import urllib.parse
import urllib.request

from adresses import nettoie
from stage_collecte import API, USER_AGENT, dep_commune
from stage_donnees import slug
from stage_nouveaux_codes import lire, publier

SOURCE = Path(__file__).with_name('lieux_choisis.json')


def etablissement(siret):
    q = dict(q=siret, per_page=1, minimal='true', include='matching_etablissements,siege')
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(q), headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        for h in json.load(r)['results']:
            for e in [h.get('siege') or {}] + (h.get('matching_etablissements') or []):
                if e.get('siret') == siret:
                    return e
    raise SystemExit('SIRET introuvable : ' + siret)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--rapport', default='lieux-choisis.json')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.write and subprocess.check_output(['git', 'branch', '--show-current'], cwd=root, text=True).strip() in ('main', 'master', ''):
        p.error('Écriture réservée à une branche de travail')
    fichiers, journal = defaultdict(list), []
    for type_, lieux in lire(SOURCE).items():
        if type_.startswith('_'):
            continue
        for lieu in lieux:
            e = etablissement(lieu['siret'])
            if e.get('etat_administratif') != 'A' or not e.get('latitude'):
                raise SystemExit('Établissement fermé ou sans position : ' + lieu['siret'])
            dep = dep_commune(e.get('commune'))
            adr, rep = nettoie(e.get('adresse') or '')
            adr = adr[0].upper() + adr[1:] if adr else adr
            if lieu.get('adresse'):  # adresse du registre peu lisible (lieu-dit, abréviations)
                adr, rep = lieu['adresse'], ''
            fichiers[(dep, slug(type_))].append([lieu['nom'], '', adr, round(float(e['latitude']), 5),
                                                 round(float(e['longitude']), 5), 0, 0, lieu['siret'], rep])
            journal.append(dict(type=type_, siret=lieu['siret'], nom=lieu['nom'], adresse=adr, dep=dep))
            time.sleep(0.3)
    fichiers = {k: sorted(v) for k, v in fichiers.items()}
    print(json.dumps(journal, ensure_ascii=False, indent=1))
    if args.write:
        publier(root, fichiers, args.rapport, dict(date=time.strftime('%Y-%m-%d'), lieux=journal))


if __name__ == '__main__':
    main()
