/* Navigateur réel, 375 px. BASE_URL pointe sur python3 -m http.server. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const BASE=(process.env.BASE_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const OUTPUT=process.env.TEST_OUTPUT||'/tmp/aide-national';fs.mkdirSync(OUTPUT,{recursive:true});
const cases=[
 ['lyon','Lyon',45.764,4.8357],['lille','Lille',50.6292,3.0573],
 ['aix-marseille','Marseille',43.2965,5.3698],['rennes','Rennes',48.1173,-1.6778],
 ['la-reunion','Saint-Denis',-20.8823,55.4504]
];
(async()=>{
 const browser=await chromium.launch();const allErrors=[];const report=[];
 async function context(options={}) {
  const c=await browser.newContext({viewport:{width:375,height:812},...options});
  const p=await c.newPage();const requests=[];
  p.on('pageerror',e=>allErrors.push(e.message));
  p.on('console',m=>{if(m.type()==='error'&&!options.expectedFailure)allErrors.push(m.text());});
  p.on('request',r=>requests.push(r.url()));
  return {c,p,requests};
 }
 async function loaded(p,slug) {
  await p.waitForFunction(slug=>location.pathname.endsWith('/'+slug+'/')&&typeof D!=='undefined'&&D!==null&&!document.querySelector('#nationalContent').hidden,slug);
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.equal(await p.locator('.ac-bar').isVisible(),true);
  assert.equal(await p.evaluate(()=>new Set(D.lieux.map(l=>l.ac)).size),1);
 }
 for(const [slug,city,lat,lon] of cases) {
  console.log('Test '+slug);
  const {c,p,requests}=await context({geolocation:{latitude:lat,longitude:lon},permissions:['geolocation']});
  await c.addInitScript(()=>localStorage.setItem('stages.academie','paris'));
  await p.goto(BASE+'/aide/'+slug+'/');await loaded(p,slug);
  assert.equal(await p.evaluate(()=>localStorage.getItem('stages.academie')),slug);
  assert(!requests.some(u=>u.includes('/aide/aide.json')),'pas de téléchargement IDF en national');
  assert(!requests.some(u=>u.includes('departements.json')),'pas de contours avant clic');
  assert(!requests.some(u=>u.includes('api-adresse')),'pas de BAN avant saisie');
  await p.locator('[data-k="tout"]').click();
  assert(new URL(p.url()).pathname.endsWith('/'+slug+'/'),'le hash ne perd pas le chemin');
  assert.equal(new URL(p.url()).hash,'#tout');
  await p.locator('#dCol').click();await p.locator('#col').fill(city);
  if(await p.locator('#csug button').count())await p.locator('#csug button').first().click();
  await p.locator('.ac-bar button').click();await p.locator('.ac-geo').click();await loaded(p,slug);
  assert(requests.some(u=>u.includes('departements.json')));
  assert(!requests.some(u=>u.includes('api-adresse')),'géolocalisation sans requête BAN');
  await p.locator('.ac-bar button').click();
  await p.locator('#ac-ville').fill(slug==='la-reunion'?'97400':city);
  await p.locator('.ac-suggestions button').first().waitFor();
  const buttons=p.locator('.ac-suggestions button');
  let picked=false;
  for(let i=0;i<await buttons.count();i++) {
   const text=await buttons.nth(i).innerText();
   if(slug!=='la-reunion'||/97400|Réunion/.test(text)){await buttons.nth(i).click();picked=true;break;}
  }
  assert(picked,'suggestion BAN adaptée');await loaded(p,slug);
  await p.locator('.ac-bar button').click();assert(await p.locator('.ac-picker').isVisible());
  await p.locator('summary').filter({hasText:'Je connais mon académie'}).click();
  await p.locator('.ac-options button').filter({hasText:slug==='la-reunion'?'La Réunion':slug==='aix-marseille'?'Aix-Marseille':city}).click();await loaded(p,slug);
  if(slug==='lyon'){await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:path.join(OUTPUT,'academie-lyon.png')});}
  const domains=[...new Set(requests.map(u=>new URL(u).hostname))];
  assert(domains.every(d=>['127.0.0.1','localhost','cdnjs.cloudflare.com','api-adresse.data.gouv.fr'].includes(d)),domains.join(','));
  report.push(slug+' : lien direct, mémoire remplacée, localisation simulée, ville BAN réelle, changer, collège, URL/hash et réseau OK');
  await c.close();
 }
 // Refus GPS, stockage indisponible, choix conservé en mémoire jusqu'au rechargement.
 {
  const {c,p}=await context();
  await c.addInitScript(()=>{
   Object.defineProperty(window,'localStorage',{get(){throw new DOMException('indisponible','SecurityError');}});
   Object.defineProperty(navigator,'geolocation',{value:{getCurrentPosition(ok,fail){fail({code:1});}}});
  });
  await p.goto(BASE+'/aide/france/');await p.locator('.ac-geo').click();
  await p.waitForFunction(()=>document.activeElement.id==='ac-ville');
  assert((await p.locator('.ac-status').innerText()).includes('Tape ta ville'));
  await p.screenshot({path:path.join(OUTPUT,'localisation-refusee.png')});
  await p.locator('summary').filter({hasText:'Je connais mon académie'}).click();
  await p.locator('.ac-options button').filter({hasText:'Lyon'}).click();await loaded(p,'lyon');
  await p.reload();await loaded(p,'lyon');await c.close();report.push('Stockage interdit et GPS refusé : repli ville, choix manuel et rechargement du lien OK');
 }
 // Mémoire commune au point d'entrée national ; root historique l'ignore et ne charge pas le module.
 {
  const {c,p,requests}=await context();await p.goto(BASE+'/aide/france/');await p.locator('.ac-picker').waitFor();
  await p.waitForFunction(()=>document.querySelectorAll('.ac-options button').length===30);
  await p.screenshot({path:path.join(OUTPUT,'question.png')});
  await p.evaluate(()=>localStorage.setItem('stages.academie','lille'));
  await p.reload();await loaded(p,'lille');
  requests.length=0;await p.goto(BASE+'/aide/#mda');await p.waitForFunction(()=>typeof D!=='undefined'&&D!==null);
  assert.equal(await p.locator('.ac-picker').count(),0);assert.equal(await p.locator('#fdep .chip').count(),3);
  assert(!requests.some(u=>u.includes('/commun/')));assert(await p.locator('.lead').innerText().then(s=>s.includes('Île-de-France')));
  await p.screenshot({path:path.join(OUTPUT,'idf-mda.png')});
  await p.goto(BASE+'/aide/');await p.waitForFunction(()=>typeof D!=='undefined'&&D!==null);await p.screenshot({path:path.join(OUTPUT,'idf.png')});
  await c.close();report.push('Mémoire commune, entrée France, Île-de-France et #mda : OK, aucun commun/ chargé sur /aide/');
 }
 assert.deepEqual(allErrors,[],'console sans erreur');
 await browser.close();fs.writeFileSync(path.join(OUTPUT,'resultat.txt'),report.join('\n')+'\nConsole : aucune erreur.\n');console.log(report.join('\n'));console.log('Console : aucune erreur.');
})().catch(e=>{console.error(e);process.exit(1);});
