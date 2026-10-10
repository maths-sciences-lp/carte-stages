"""Liens courts et page du lycée Eugène Hénaff : python3 raccourcis.py <dossier du site>

Chaque lien court compte sa propre visite (GoatCounter, chemin /era/, /tne/…) avant de renvoyer vers la carte."""
import json,sys,os,html
OUT=sys.argv[1]; UAI='0932119Y'
R=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'raccourcis_henaff.json')))
R['ma']=R['tma']
idx=json.load(open(os.path.join(OUT,'data','index.json'))); F={f['k']:f for f in idx['formations']}
def cible(code): return f"../#ly={UAI}&f={R[code]}"
for code in R:
    d=os.path.join(OUT,code); os.makedirs(d,exist_ok=True)
    u=cible(code)
    open(os.path.join(d,'index.html'),'w').write(f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trouve ton stage</title><meta http-equiv="refresh" content="0;url={u}"><meta name="robots" content="noindex">
<script>if(!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname)&&navigator.sendBeacon)navigator.sendBeacon("https://maths-sciences.goatcounter.com/count?p="+encodeURIComponent(location.pathname)+"&t="+encodeURIComponent("Lien de classe")+"&r="+encodeURIComponent(document.referrer)+"&rnd="+Math.random().toString(36).slice(2));location.replace("{u}")</script><link rel="icon" href="/commun/logo.svg" type="image/svg+xml"></head><body><p><a href="{u}">Ouvrir la carte des stages</a></p></body></html>
''')
GROUPES=[("Seconde",["tne","mnb","mama"],{"tne":"2nde TNE","mnb":"2nde MNB","mama":"2nde MAMA"}),
 ("Bac pro (1re et terminale)",["iccer","mee","tma","era","eeb","geometre"],{"iccer":"ICCER","mee":"MEE","tma":"TMA (menuisier agenceur)","era":"ERA (agencement)","eeb":"EEB (études du bâtiment)","geometre":"Géomètre"}),
 ("CAP",["mit","sdg","ebeniste"],{"mit":"CAP MIT","sdg":"CAP Signalétique","ebeniste":"CAP Ébéniste"}),
 ("BMA",["bma-ebeniste","bma-signaletique"],{"bma-ebeniste":"BMA Ébéniste","bma-signaletique":"BMA Signalétique"})]
def ico(nom): return f'<svg class="ico" width="1.2em" height="1.2em" aria-hidden="true" focusable="false"><use href="/commun/icones.svg#{nom}"/></svg>'
SECONDES={'tne','mnb','mama'}  # après la 2nde : la 1re au lycée, pas de poursuite d'études
blocs=''
for titre,codes,lab in GROUPES:
    def carte(c):
        apres='' if c in SECONDES else f'<a class="bt" href="../formation/#{c}">{ico('formation')} Après mon diplôme</a>'
        return (f'<div class="cl"><b>{html.escape(lab[c])}</b><span>{html.escape(F[R[c]]["t"]+" "+F[R[c]]["n"])}</span>'
                f'<div class="bts"><a class="bt" href="../{c}/">{ico('stage')} Mon stage</a>{apres}</div></div>')
    btns=''.join(carte(c) for c in codes)
    blocs+=f'<h2>{html.escape(titre)}</h2><div class="grid">{btns}</div>'
os.makedirs(os.path.join(OUT,'henaff'),exist_ok=True)
open(os.path.join(OUT,'henaff','index.html'),'w').write(f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lycée Eugène Hénaff – Stages et orientation</title>
<link rel="stylesheet" href="../fonts/fonts.css">
<style>
:root{{--ink:#15314f;--bg:#f5f7f9;--line:#e4e9ee;--mute:#667085;--card:#fff;--acc:#2a4f7c}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.45 'Public Sans',system-ui,sans-serif}}
.site{{display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--card);border-bottom:1px solid var(--line);color:var(--ink);text-decoration:none}}
.site .lg{{width:32px;height:32px;border-radius:9px;background:var(--ink);display:grid;place-items:center;color:#fff}}
.site b{{font-family:'Bricolage Grotesque',system-ui;font-size:17px}}.site span.r{{margin-left:auto;font-size:14px;color:var(--mute)}}
main{{max-width:760px;margin:0 auto;padding:18px 16px 30px}}
h1{{font-family:'Bricolage Grotesque',system-ui;font-size:26px;margin:4px 0 4px}}
.lead{{color:var(--mute);margin:0 0 6px}}
h2{{font-family:'Bricolage Grotesque',system-ui;font-size:19px;margin:22px 0 10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}}
.cl{{display:flex;flex-direction:column;gap:3px;padding:14px 16px;background:var(--card);border:2px solid var(--line);border-radius:16px;color:var(--ink);min-height:76px}}
.bts{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
.bt{{display:inline-flex;align-items:center;gap:4px;min-height:44px;box-sizing:border-box;padding:8px 12px;border:2px solid var(--line);border-radius:12px;color:var(--ink);text-decoration:none;font-size:15px;font-weight:600}}
.bt:hover,.bt:focus-visible{{border-color:var(--acc)}}
.cl b{{font-size:19px}}.cl>span{{font-size:14px;color:var(--mute);line-height:1.3}}
.autre{{display:inline-block;margin-top:26px;color:var(--acc)}}
.credit{{margin-top:22px;font-size:13px;color:var(--mute)}}
</style>
<script>if(!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname)){{var g=document.createElement('script');g.async=true;g.dataset.goatcounter='https://maths-sciences.goatcounter.com/count';g.src='https://gc.zgo.at/count.js';document.head.appendChild(g);}}</script>
<link rel="stylesheet" href="../commun/accessibilite.css">
<link rel="stylesheet" href="/commun/navigation.css">
<link rel="icon" href="/commun/logo.svg" type="image/svg+xml">
</head><body>
<a class="skip-link" href="#contenu-principal">Aller au contenu principal</a>
<header class="entete"><a class="site" href="/accueil/"><span class="lg"><svg width="34" height="34" viewBox="0 0 112 112" aria-hidden="true" focusable="false"><rect width="112" height="112" rx="28" fill="#15314f"/><path d="M56 92s-26-22-26-44a26 26 0 0 1 52 0c0 22-26 44-26 44z" fill="none" stroke="#fff" stroke-width="8" stroke-linejoin="round"/><circle cx="56" cy="47" r="11" fill="#E8590C"/></svg></span><span class="nom"><b>Stages et orientation</b><small>Maths·Sciences</small></span></a><a class="r" href="/accueil/">← Tous les outils</a></header>
<main id="contenu-principal" tabindex="-1">
<h1>{ico('lycee')} Lycée Eugène Hénaff</h1>
<p class="lead"><b>Trouve ta classe</b>, puis choisis : <b>{ico('stage')} Mon stage</b> ouvre la carte des entreprises de ton métier, au départ du lycée ; <b>{ico('formation')} Après mon diplôme</b> montre les poursuites d’études possibles.</p>
{blocs}
<a class="autre" href="../">Une autre formation ? Ouvrir la carte complète →</a>
<a class="autre" href="../formation/" style="margin-left:0;display:block;margin-top:12px">{ico('formation')} Après le lycée : toutes les formations →</a>
<a class="autre" href="../aide/" style="margin-left:0;display:block;margin-top:12px">{ico('aide')} Qui peut m’aider ? Orientation, emploi, un endroit pour travailler, besoin de parler →</a>
<footer>
<div data-pied-commun></div><p class="credit">© 2026 Naïm Azzouz · Lycée Eugène Hénaff, Bagnolet (93) · Académie de Créteil</p>
</footer>
</main><script src="../commun/accessibilite.js"></script>
<script type="module" src="/commun/pied.js"></script>
</body></html>
''')
print(len(R),'liens courts + page henaff')
