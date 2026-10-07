"""Liens courts et page du lycée Eugène Hénaff : python3 raccourcis.py <dossier du site>"""
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
<script>location.replace("{u}")</script></head><body><p><a href="{u}">Ouvrir la carte des stages</a></p></body></html>
''')
GROUPES=[("Seconde",["tne","mnb","mama"],{"tne":"2nde TNE","mnb":"2nde MNB","mama":"2nde MAMA"}),
 ("Bac pro (1re et terminale)",["iccer","mee","tma","era","eeb","geometre"],{"iccer":"ICCER","mee":"MEE","tma":"TMA (menuisier agenceur)","era":"ERA (agencement)","eeb":"EEB (études du bâtiment)","geometre":"Géomètre"}),
 ("CAP",["mit","sdg","ebeniste"],{"mit":"CAP MIT","sdg":"CAP Signalétique","ebeniste":"CAP Ébéniste"}),
 ("BMA",["bma-ebeniste","bma-signaletique"],{"bma-ebeniste":"BMA Ébéniste","bma-signaletique":"BMA Signalétique"})]
blocs=''
for titre,codes,lab in GROUPES:
    btns=''.join(f'<a class="cl" href="../{c}/"><b>{html.escape(lab[c])}</b><span>{html.escape(F[R[c]]["t"]+" "+F[R[c]]["n"])}</span></a>' for c in codes)
    blocs+=f'<h2>{html.escape(titre)}</h2><div class="grid">{btns}</div>'
os.makedirs(os.path.join(OUT,'henaff'),exist_ok=True)
open(os.path.join(OUT,'henaff','index.html'),'w').write(f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trouve ton stage – Lycée Eugène Hénaff</title>
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
.cl{{display:flex;flex-direction:column;gap:3px;padding:14px 16px;background:var(--card);border:2px solid var(--line);border-radius:16px;color:var(--ink);text-decoration:none;min-height:76px}}
.cl:hover,.cl:focus-visible{{border-color:var(--acc);outline:none}}
.cl b{{font-size:19px}}.cl span{{font-size:14px;color:var(--mute);line-height:1.3}}
.autre{{display:inline-block;margin-top:26px;color:var(--acc)}}
.credit{{margin-top:22px;font-size:13px;color:var(--mute)}}
</style>
<script>if(!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname)){{var g=document.createElement('script');g.async=true;g.dataset.goatcounter='https://maths-sciences.goatcounter.com/count';g.src='https://gc.zgo.at/count.js';document.head.appendChild(g);}}</script>
<link rel="stylesheet" href="../commun/accessibilite.css">
</head><body>
<a class="skip-link" href="#contenu-principal">Aller au contenu principal</a>
<header><a class="site" href="https://maths-sciences-pro.fr/"><span class="lg" aria-hidden="true"><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3v15a1 1 0 0 0 1 1h15"/><path d="M5 15c3 0 4.5-8 8-8s3.8 5 7 3"/></svg></span><b>Maths<span style="color:var(--mute)">·</span>Sciences</b><span class="r">← Retour au site</span></a></header>
<main id="contenu-principal" tabindex="-1">
<h1>🎯 Trouve ton stage</h1>
<p class="lead">Lycée Eugène Hénaff · <b>Appuie sur ta classe</b> : la carte s’ouvre avec les entreprises de ton métier, au départ du lycée.</p>
{blocs}
<a class="autre" href="../">Une autre formation ? Ouvrir la carte complète →</a>
<a class="autre" href="../formation/" style="margin-left:0;display:block;margin-top:12px">🎓 Après le lycée : trouve ta formation →</a>
<footer><p class="credit"><a href="../faq/">Questions fréquentes</a> · <a href="../faq/#vie-privee">Vie privée</a> · <a href="../accessibilite/">Accessibilité</a> · <a href="https://maths-sciences-pro.fr/confidentialite">Confidentialité</a><br>© 2026 Naïm Azzouz · Lycée Eugène Hénaff, Bagnolet (93) · Académie de Créteil</p>
</footer>
</main><script src="../commun/accessibilite.js"></script>
</body></html>
''')
print(len(R),'liens courts + page henaff')
