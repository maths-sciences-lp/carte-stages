"""Non-régression Île-de-France : caches historiques, origin/main, navigateur 375 px.
Python standard + Node/Playwright (PLAYWRIGHT_MODULE si installation hors dépôt).
Aucun fichier du dépôt n'est réécrit. Codes de sortie : 0 vérifié, 1 différence,
2 vérification incomplète. Rapport et captures dans --rapport (hors dépôt par défaut).
"""
import argparse
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['/aide/', '/aide/#mda', '/apres-3e/', '/apres-3e/#cuisine', '/formation/',
         '/formation/#eeb', '/formation/#iccer', '/', '/henaff/', '/iccer']
DATA = ['aide/aide.json', 'apres-3e/apres3e.json', 'formation/formations.json']
DATA.append('formation/parcoursup.json')
PAGES += ['/formation/#'+k for k in ['mee','tma','era','geometre','mit','sdg','ebeniste','bma-ebeniste','bma-signaletique']]
PAGES.append('/formation/#d=5601&ly=0932119Y')
BROWSER = r'''
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
(async()=>{
 const browser=await chromium.launch({headless:true});const rows=[];
 for(let i=0;i<cfg.pages.length;i++) {
  const suffix=cfg.pages[i];const states=[];
  for(const [label,base] of [['local',cfg.local],['en-ligne',cfg.online]]) {
   const context=await browser.newContext({viewport:{width:375,height:812},deviceScaleFactor:1});
   // La mesure de visites est sans effet sur le contenu ; pas de fausses visites.
   await context.route(/goatcounter|gc\.zgo\.at/,r=>r.fulfill({status:204,body:''}));
   const page=await context.newPage();const errors=[];
   page.on('pageerror',e=>errors.push('JavaScript : '+e.message));
   page.on('console',m=>{if(m.type()==='error')errors.push('Console : '+m.text());});
   page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url());});
   try {
    const response=await page.goto(base.replace(/\/$/,'')+suffix,{waitUntil:'networkidle',timeout:60000});
    if(!response?.ok())throw Error('HTTP '+response?.status());
    if(/^\/(aide|apres-3e|formation)\//.test(suffix))await page.waitForFunction(()=>typeof D!=='undefined'&&D!==null);
    await page.evaluate(()=>document.fonts.ready);
    // Attend la stabilisation du texte après les redirections et chargements différés.
    let before='',stable=0;
    for(let tries=0;tries<30&&stable<3;tries++) {
     const text=await page.locator('body').innerText();stable=text===before?stable+1:0;before=text;await page.waitForTimeout(200);
    }
    await page.screenshot({path:path.join(cfg.output,`${String(i+1).padStart(2,'0')}-${label}.png`),fullPage:true});
    const state=await page.evaluate(()=>({text:document.body.innerText,
     fields:[...document.querySelectorAll('input,select,button[aria-pressed]')].map(e=>[e.id,e.value||'',e.getAttribute('aria-pressed')]),
     width:document.documentElement.scrollWidth, viewport:innerWidth}));
    states.push({...state,errors,url:page.url()});
   } catch(e){states.push({errors:[...errors,e.message]});}
   await context.close();
  }
  const equal=states.every(s=>s.text!==undefined)&&states[0].text===states[1].text&&JSON.stringify(states[0].fields)===JSON.stringify(states[1].fields);
  const ok=equal&&states.every(s=>s.errors.length===0);
  rows.push({page:suffix,identique:equal,sans_erreur:states.every(s=>s.errors.length===0),etats:states});
  console.log(suffix+' : '+(ok?'identique, sans erreur':'DIFFÉRENCE OU ERREUR'));
 }
 await browser.close();fs.writeFileSync(path.join(cfg.output,'pages.json'),JSON.stringify(rows,null,2));
})().catch(e=>{console.error(e);process.exit(1);});
'''

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources-idf',type=Path,help='Dossier des sources historiques : annuaire-sp.json, bibliotheques.json, colleges_idf.json (ou colleges.json)')
    parser.add_argument('--sources-apres3e',type=Path,help='Cache historique : 605340ddc19a9.csv, ij.json, annuaire_hebergement.json, pression_2025.json, colleges_idf.json (ou colleges.json)')
    parser.add_argument('--sources-formation',type=Path,help='Cache historique : 605340ddc19a9.csv, sup2.csv, ij.json et fiches/')
    parser.add_argument('--rapport',type=Path,default=Path(tempfile.gettempdir())/'verif-idf')
    parser.add_argument('--en-ligne',default='https://maths-sciences-lp.github.io/carte-stages',help='Déploiement canonique du dépôt ; /stages/ est un accueil distinct sur le domaine personnalisé')
    args=parser.parse_args();out=args.rapport.resolve();out.mkdir(parents=True,exist_ok=True)
    lines=[];differences=[];incomplet=[]
    def log(s):
        lines.append(s);print(s,flush=True)
    ref=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip()
    log('Référence origin/main : '+ref)
    for name in DATA:
        expected=subprocess.check_output(['git','show',ref+':'+name],cwd=ROOT)
        actual=(ROOT/name).read_bytes()
        equal=actual==expected
        log(f'{name} : '+('identique à origin/main' if equal else 'DIFFÉRENT de origin/main')+' ; SHA-256 '+hashlib.sha256(actual).hexdigest())
        if not equal:differences.append(name)
    # Exécute réellement le mode par défaut, dans un dossier temporaire isolé.
    with tempfile.TemporaryDirectory(prefix='regen-idf-') as tmp:
        tmp=Path(tmp)
        if args.sources_idf:
            for name in ['annuaire-sp.json','bibliotheques.json','colleges_idf.json','colleges.json']:
                p=args.sources_idf/name
                if p.exists():shutil.copy2(p,tmp/name)
        result=subprocess.run([sys.executable,str(ROOT/'source/aide.py')],cwd=tmp,capture_output=True,text=True)
        generated=tmp/'aide.json'
        if result.returncode or not generated.exists():
            detail=(result.stderr or result.stdout).strip().splitlines()[-1]
            log('Régénération aide (mode par défaut) : NON VÉRIFIÉE — '+detail)
            incomplet.append('Régénération aide : sources historiques manquantes ou erreur (voir ci-dessus)')
        else:
            expected=subprocess.check_output(['git','show',ref+':aide/aide.json'],cwd=ROOT)
            same=generated.read_bytes()==expected
            log('Régénération aide (mode par défaut) : '+('identique à l’octet près' if same else 'DIFFÉRENTE — consulter le fichier régénéré'))
            if not same:
                shutil.copy2(generated,out/'aide-regenere.json');differences.append('aide régénéré')
    with tempfile.TemporaryDirectory(prefix='regen-apres3e-idf-') as tmp:
        tmp=Path(tmp)
        if args.sources_apres3e:
            for name in ['605340ddc19a9.csv','ij.json','annuaire_hebergement.json','pression_2025.json','colleges_idf.json','colleges.json']:
                p=args.sources_apres3e/name
                if p.exists():shutil.copy2(p,tmp/name)
        # Le mode historique accepte l'absence de pression ; le contrôle, lui,
        # l'annonce explicitement au lieu de prétendre avoir toutes les sources.
        required=['605340ddc19a9.csv','ij.json','annuaire_hebergement.json','pression_2025.json']
        missing=[n for n in required if not (tmp/n).exists()]
        if not any((tmp/n).exists() for n in ['colleges_idf.json','colleges.json']):missing.append('colleges_idf.json ou colleges.json')
        if missing:
            log('Régénération Après le collège (mode par défaut) : NON VÉRIFIÉE — sources manquantes : '+', '.join(missing))
            incomplet.append('Régénération Après le collège : sources historiques manquantes')
        else:
            result=subprocess.run([sys.executable,str(ROOT/'source/apres3e.py')],cwd=tmp,capture_output=True,text=True)
            generated=tmp/'apres3e.json'
            if result.returncode or not generated.exists():
                detail=(result.stderr or result.stdout or 'Aucun fichier produit').strip().splitlines()[-1]
                log('Régénération Après le collège (mode par défaut) : NON VÉRIFIÉE — '+detail)
                incomplet.append('Régénération Après le collège : erreur')
            else:
                expected=subprocess.check_output(['git','show',ref+':apres-3e/apres3e.json'],cwd=ROOT)
                same=generated.read_bytes()==expected
                log('Régénération Après le collège (mode par défaut) : '+('identique à l’octet près' if same else 'DIFFÉRENTE — consulter apres3e-regenere.json'))
                if not same:
                    shutil.copy2(generated,out/'apres3e-regenere.json');differences.append('apres3e régénéré')
    with tempfile.TemporaryDirectory(prefix='regen-formation-idf-') as tmp:
        tmp=Path(tmp)
        if args.sources_formation:
            for name in ['605340ddc19a9.csv','sup2.csv','ij.json']:
                p=args.sources_formation/name
                if p.exists():shutil.copy2(p,tmp/name)
            p=args.sources_formation/'fiches'
            if p.exists():shutil.copytree(p,tmp/'fiches')
        result=subprocess.run([sys.executable,str(ROOT/'source/apres_lycee.py')],cwd=tmp,capture_output=True,text=True)
        generated=tmp/'formations.json'
        if result.returncode or not generated.exists():
            log('Régénération Après le lycée (mode par défaut) : NON VÉRIFIÉE — '+(result.stderr or result.stdout or 'Aucune sortie').strip().splitlines()[-1])
            incomplet.append('Régénération Après le lycée : sources historiques manquantes ou erreur')
        else:
            expected=subprocess.check_output(['git','show',ref+':formation/formations.json'],cwd=ROOT)
            same=generated.read_bytes()==expected
            log('Régénération Après le lycée (mode par défaut) : '+('identique à l’octet près' if same else 'DIFFÉRENTE — consulter formations-regenere.json'))
            if not same:
                shutil.copy2(generated,out/'formations-regenere.json');differences.append('formations régénéré')
        # Parcoursup écrit à côté de son script : isoler aussi cette arborescence.
        (tmp/'source').mkdir();(tmp/'formation').mkdir()
        shutil.copy2(ROOT/'source/parcoursup.py',tmp/'source/parcoursup.py')
        shutil.copy2(generated if generated.exists() else ROOT/'formation/formations.json',tmp/'formation/formations.json')
        result=subprocess.run([sys.executable,str(tmp/'source/parcoursup.py')],cwd=tmp,capture_output=True,text=True)
        ps=tmp/'formation/parcoursup.json'
        if result.returncode or not ps.exists():
            log('Régénération Parcoursup (mode par défaut) : NON VÉRIFIÉE — '+(result.stderr or result.stdout or 'Aucune sortie').strip().splitlines()[-1])
            incomplet.append('Parcoursup : source distante indisponible ou erreur')
        else:
            expected=subprocess.check_output(['git','show',ref+':formation/parcoursup.json'],cwd=ROOT)
            same=ps.read_bytes()==expected
            log('Régénération Parcoursup (mode par défaut) : '+('identique à l’octet près' if same else 'DIFFÉRENTE — consulter parcoursup-regenere.json'))
            if not same:
                shutil.copy2(ps,out/'parcoursup-regenere.json');differences.append('Parcoursup régénéré')
    handler=functools.partial(QuietHandler,directory=str(ROOT))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    config=dict(pages=PAGES,local=f'http://127.0.0.1:{server.server_port}',online=args.en_ligne,output=str(out))
    (out/'config.json').write_text(json.dumps(config));(out/'navigateur.cjs').write_text(BROWSER)
    # Un ancien résultat ne peut jamais faire passer une exécution en échec.
    (out/'pages.json').unlink(missing_ok=True)
    try:
        result=subprocess.run(['node',str(out/'navigateur.cjs'),str(out/'config.json')],capture_output=True,text=True)
        log(result.stdout.strip())
        if result.returncode or not (out/'pages.json').exists():
            log('Comparaison navigateur INCOMPLÈTE : '+result.stderr.strip());incomplet.append('Navigateur')
        else:
            rows=json.loads((out/'pages.json').read_text())
            for row in rows:
                if not row['identique'] or not row['sans_erreur']:
                    differences.append(row['page']);log(json.dumps(row,ensure_ascii=False))
    finally:
        server.shutdown();server.server_close()
    ok=not differences and not incomplet
    log('Île-de-France identique : '+('oui' if ok else 'non'))
    if incomplet:log('Vérification complète non établie : '+' ; '.join(incomplet)+'. Ne pas confondre avec une différence constatée.')
    if differences:log('Différences ou erreurs constatées : '+', '.join(differences))
    log('Rapport et captures : '+str(out))
    (out/'resume.txt').write_text('\n'.join(lines)+'\n')
    return 1 if differences else 2 if incomplet else 0

if __name__=='__main__':
    sys.exit(main())
