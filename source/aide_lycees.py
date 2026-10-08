"""« Qui peut m'aider ? » : départ « Mon lycée ».

Lycées ouverts de l'annuaire de l'Éducation nationale (généraux, technologiques,
professionnels, publics et privés), un fichier par académie : aide/data/lycees/<slug>.json.
Téléchargé seulement quand l'élève appuie sur « Mon lycée » : la page par défaut ne change pas.
Un lycée et une section qui partagent le même UAI restent deux choix s'ils ont un autre nom.

python3 source/aide_lycees.py [--cache DOSSIER]   (lancé aussi à la fin de aide.py --academies toutes)
"""
import argparse
import datetime
import json
from pathlib import Path
import urllib.parse

from aide import CATALOGUE, EDU, coords, get_json, nom_court, write_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'aide/data/lycees'
URL = EDU + '?' + urllib.parse.urlencode(dict(
    where='type_etablissement="Lycée" and etat="OUVERT"',
    select='identifiant_de_l_etablissement,nom_etablissement,nom_commune,latitude,longitude,code_departement'))


def dep(code):
    code = str(code or '')
    return code.lstrip('0').zfill(2) if not code.startswith('97') and not code.startswith('097') else code.lstrip('0')


def main(cache=None):
    cache = Path(cache or Path.home()/'.cache'/'carte-stages-aide').expanduser()
    lignes = get_json(URL, cache/'lycees-national.json')
    acad = {d: ac['slug'] for ac in CATALOGUE for d in ac['deps']}
    par_ac, hors = {ac['slug']: {} for ac in CATALOGUE}, 0
    for r in lignes:
        c = coords(r['latitude'], r['longitude'])
        s = acad.get(dep(r['code_departement']))
        if not c or not s:
            hors += 1
            continue
        cle = (r['identifiant_de_l_etablissement'], r['nom_etablissement'], r['nom_commune'])
        par_ac[s][cle] = dict(n=r['nom_etablissement'], v=' '.join(r['nom_commune'].split()), u=r['identifiant_de_l_etablissement'], **c)
    bilan = []
    for s, ly in par_ac.items():
        if not ly:
            raise ValueError('Aucun lycée : ' + s)
        liste = sorted(ly.values(), key=lambda x: (x['n'], x['v']))
        write_json(OUT/f'{s}.json', dict(date=datetime.date.today().isoformat(), lycees=liste))
        bilan.append(dict(slug=s, academie=nom_court(next(a for a in CATALOGUE if a['slug'] == s)), lycees=len(liste)))
    (OUT/'bilan.json').write_text(json.dumps(dict(source=URL, ecartes_sans_position_ou_hors_catalogue=hors, academies=bilan),
                                             ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(sum(b['lycees'] for b in bilan), 'lycées ;', hors, 'écartés')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path)
    main(p.parse_args().cache)
