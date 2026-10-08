#!/usr/bin/env python3
"""Surveillance nocturne des outils « Stages et orientation ».

Vérifie que les pages et les données publiées répondent, que les fichiers JSON
se lisent, et que La bonne alternance a été mise à jour depuis moins de 40 jours.
Sortie non nulle au moindre problème : GitHub prévient alors le propriétaire du
dépôt par mail. Aucune donnée personnelle, aucune clé.
"""
import json, sys, time, urllib.request
from datetime import datetime, timezone

SITE = 'https://maths-sciences-lp.github.io/carte-stages/'
DONNEES = 'https://maths-sciences-lp.github.io/carte-stages-donnees/'
DOMAINE = 'https://maths-sciences-pro.fr/stages/'
OUTILS = ('stage', 'aide', 'apres-3e', 'formation')
CLASSES = ('tne', 'mnb', 'mama', 'iccer', 'mee', 'era', 'tma', 'eeb', 'geometre',
           'mit', 'sdg', 'ebeniste', 'bma-ebeniste', 'bma-signaletique', 'ma')
PAGES = ('', 'accueil/', 'henaff/', 'faq/', 'demo/', 'accessibilite/')
LBA_MAX_JOURS = 40
UA = {'User-Agent': 'Mozilla/5.0 (surveillance carte-stages)'}
problemes = []


def lire(url, essais=3):
    for n in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.status, r.read()
        except Exception as e:  # erreur réseau ou HTTP : nouvel essai
            err = e
            time.sleep(3 * (n + 1))
    return getattr(err, 'code', 0), b''


def page(url):
    code, _ = lire(url)
    if code != 200:
        problemes.append(f'Page {url} : code {code}')


def donnees(url):
    code, corps = lire(url)
    if code != 200:
        problemes.append(f'Données {url} : code {code}')
        return None
    try:
        return json.loads(corps)
    except ValueError:
        problemes.append(f'Données {url} : JSON illisible')
        return None


def fraicheur(url, nom):
    meta = donnees(url)
    if not meta:
        return
    date = datetime.fromisoformat(meta['updated_at'].replace('Z', '+00:00'))
    jours = (datetime.now(timezone.utc) - date).days
    if jours > LBA_MAX_JOURS:
        problemes.append(f'La bonne alternance ({nom}) : dernière mise à jour il y a {jours} jours')


academies = [a['slug'] for a in donnees(SITE + 'commun/academies.json') or []]
if len(academies) != 30:
    problemes.append(f'Catalogue des académies : {len(academies)} au lieu de 30')
for p in PAGES:
    page(SITE + p)
for c in CLASSES:
    page(SITE + c + '/')
for outil in OUTILS:
    for slug in ('france', *academies):
        page(f'{SITE}{outil}/{slug}/')
for outil in ('aide', 'apres-3e', 'formation'):
    for slug in academies:
        donnees(f'{SITE}{outil}/data/{slug}.json')
catalogue = donnees(DONNEES + 'catalogue.json')
if catalogue:
    if not catalogue.get('complet'):
        problemes.append('Données nationales : catalogue marqué incomplet')
    for dep, d in sorted(catalogue['departements'].items()):
        fichiers = [k for k, v in d.get('secteurs', {}).items() if v.get('n')]
        if fichiers:  # un fichier d'entreprises par département suffit à détecter une panne
            donnees(f'{DONNEES}sirene/{dep}/{fichiers[0]}.json')
# La carte IDF et les cartes nationales lisent désormais le même export LBA.
# data/lba reste une archive : sa date ne doit pas déclencher une fausse alerte.
for nom in ('catalogue-leger.json', 'catalogues/ile-de-france.json'):
    leger = donnees(DONNEES + nom)
    if leger and leger.get('format') != 'leger-v1':
        problemes.append(f'Catalogue léger incompatible : {nom}')
fraicheur(DONNEES + 'lba/meta.json', 'France')
code, _ = lire(DOMAINE)
if code != 200:
    problemes.append(f'Adresse publique {DOMAINE} : code {code}')

if problemes:
    print(f'{len(problemes)} problème(s) :')
    print('\n'.join('- ' + p for p in problemes))
    sys.exit(1)
print('Tout répond : pages, données et mises à jour La bonne alternance.')
