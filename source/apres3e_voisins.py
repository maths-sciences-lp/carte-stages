"""« Après le collège » : lycées des académies voisines (mission 8.6).

Pour chaque académie, apres-3e/data/<slug>-voisins.json réunit les offres des autres
académies dont le lycée est à moins de RAYON km de la limite de l'académie (contours
des départements, commun/contours/). Même forme que les fichiers d'académie ; chaque
lieu porte « x »: 1 (autre académie). Les premiers vœux (« p », Draio Créteil) sont
retirés : ils ne concernent que l'affectation dans l'académie de Créteil.
Un fichier ile-de-france-voisins.json sert la page Île-de-France (/apres-3e/).

Le fichier n'est téléchargé que si l'élève appuie sur « Montrer aussi les lycées
proches d'une autre académie » : la page par défaut ne change pas.

python3 source/apres3e_voisins.py   (après apres3e.py --academies toutes)
"""
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'apres-3e/data'
RAYON = 30  # km, décision du 8/10/2026
IDF = ('creteil', 'paris', 'versailles')


def segments(deps):
    """Segments (lon1, lat1, lon2, lat2) des contours des départements."""
    out = []
    for d in deps:
        g = json.loads((ROOT/'commun/contours'/f'{d}.json').read_text())['geometry']
        for poly in ([g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']):
            for ring in poly:
                out += [(a[0], a[1], b[0], b[1]) for a, b in zip(ring, ring[1:])]
    return out


def distance_km(lat, lon, segs):
    """Distance du point au contour le plus proche (projection locale, précision < 1 %)."""
    kx, ky = 111.32*math.cos(math.radians(lat)), 110.574
    best = math.inf
    for x1, y1, x2, y2 in segs:
        ax, ay = (x1-lon)*kx, (y1-lat)*ky
        bx, by = (x2-lon)*kx, (y2-lat)*ky
        dx, dy = bx-ax, by-ay
        t = 0 if dx == dy == 0 else max(0, min(1, -(ax*dx+ay*dy)/(dx*dx+dy*dy)))
        px, py = ax+t*dx, ay+t*dy
        d = px*px+py*py
        if d < best:
            best = d
    return math.sqrt(best)


def dedans(lat, lon, d):
    """Le point est-il dans le département d (contour officiel, test du rayon) ?"""
    g = json.loads((ROOT/'commun/contours'/f'{d}.json').read_text())['geometry']
    for poly in ([g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']):
        c = False
        for ring in poly:
            for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
                if (y1 > lat) != (y2 > lat) and lon < (x2-x1)*(lat-y1)/(y2-y1)+x1:
                    c = not c
        if c:
            return True
    return False


def bien_place(e, cache={}):
    """Écarte les lycées dont les coordonnées Onisep tombent loin de leur propre département
    (ex. École Terrade Nice placée près d'Alençon) : à plus de 5 km de son contour."""
    if e['o'] not in cache:
        d = e['cp'][:3] if e['cp'].startswith('97') else e['cp'][:2]
        if d == '20':
            d = '2A' if int(e['cp']) < 20200 else '2B'
        chemin = ROOT/'commun/contours'/f'{d}.json'
        cache[e['o']] = (not chemin.exists() or dedans(e['lat'], e['lon'], d)
                         or distance_km(e['lat'], e['lon'], segments([d])) <= 5)
    return cache[e['o']]


def main():
    catalog = json.loads((ROOT/'commun/academies.json').read_text())
    data = {a['slug']: json.loads((DATA/f"{a['slug']}.json").read_text()) for a in catalog}
    groupes = [(a['slug'], (a['slug'],), a['deps']) for a in catalog]
    groupes.append(('ile-de-france', IDF, [d for a in catalog if a['slug'] in IDF for d in a['deps']]))
    bilan, mal_places = [], {}
    for slug, membres, deps in groupes:
        segs = segments(deps)
        lons = [v for s in segs for v in (s[0], s[2])]
        lats = [v for s in segs for v in (s[1], s[3])]
        marge_lat = RAYON/110.574
        marge_lon = RAYON/(111.32*math.cos(math.radians(max(abs(min(lats)), abs(max(lats))))))
        boite = (min(lons)-marge_lon, min(lats)-marge_lat, max(lons)+marge_lon, max(lats)+marge_lat)
        proches = {}  # lycée (lien Onisep) -> distance, calculée une fois
        formations = {}
        for autre, d in data.items():
            if autre in membres:
                continue
            for f in d['formations']:
                for e in f['e']:
                    if not (boite[0] <= e['lon'] <= boite[2] and boite[1] <= e['lat'] <= boite[3]):
                        continue
                    if not bien_place(e):
                        mal_places[e['o']] = dict(n=e['n'], cp=e['cp'], v=e['v'], lat=e['lat'], lon=e['lon'], o=e['o'])
                        continue
                    if e['o'] not in proches:
                        proches[e['o']] = distance_km(e['lat'], e['lon'], segs)
                    if proches[e['o']] > RAYON:
                        continue
                    g = formations.setdefault(f['n'], {k: v for k, v in f.items() if k not in ('e', 'du', 'duv')} | {'e': []})
                    x = {k: v for k, v in e.items() if k != 'p'}
                    x['du'] = e.get('du', f['du'])  # durée explicite : la formation voisine peut avoir une autre durée par défaut
                    x['x'] = 1
                    g['e'].append(x)
        rang = {'2de pro': 0, 'Bac pro': 1, 'CAP': 2}
        out = dict(rayon_km=RAYON, formations=sorted(formations.values(), key=lambda f: (rang[f['t']], f['n'])))
        path = DATA/f'{slug}-voisins.json'
        path.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
        lycees = {e['o'] for f in out['formations'] for e in f['e']}
        acs = sorted({e['ac'] for f in out['formations'] for e in f['e']})
        bilan.append(dict(slug=slug, lycees=len(lycees), offres=sum(len(f['e']) for f in out['formations']),
                          formations=len(out['formations']), academies_voisines=acs,
                          octets=path.stat().st_size, gzip_octets=len(gzip.compress(path.read_bytes(), mtime=0))))
        print(bilan[-1], flush=True)
    (DATA/'bilan-voisins.json').write_text(json.dumps(dict(rayon_km=RAYON, academies=bilan,
        coordonnees_incoherentes=sorted(mal_places.values(), key=lambda x: x['n'])), ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
