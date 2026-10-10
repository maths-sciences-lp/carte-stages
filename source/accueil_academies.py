"""Pages /accueil/<académie>/ et /accueil/france/ : python3 source/accueil_academies.py (depuis la racine du dépôt)."""
import json,os,html
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
acs=json.load(open(os.path.join(ROOT,'commun','academies.json')))
def page(slug,titre):
    d=os.path.join(ROOT,'accueil',slug);os.makedirs(d,exist_ok=True)
    open(os.path.join(d,'index.html'),'w').write(f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stages et orientation – {html.escape(titre)}</title><link rel="stylesheet" href="../../commun/accessibilite.css"><link rel="icon" href="/commun/logo.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/commun/logo-180.png"><link rel="manifest" href="/commun/site.webmanifest"><meta name="theme-color" content="#15314f"></head><body><main><p id="loading" role="status">Chargement…</p><noscript>Active JavaScript pour régler les outils sur ton académie, ou <a href="../">ouvre l’accueil</a>.</noscript></main><footer><a href="../../accessibilite/">Accessibilité</a></footer><script src="../ouvrir.js"></script></body></html>
''')
page('france','France')
for a in acs: page(a['slug'],a['nom'])
print(len(acs)+1,'pages')
