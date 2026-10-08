/* Navigateur réel, 375 px. BASE_URL pointe sur python3 -m http.server. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const BASE=(process.env.BASE_URL||'http://127.0.0.1:8766').replace(/\/$/,'');
const OUTPUT=process.env.TEST_OUTPUT||'/tmp/apres3e-national';fs.mkdirSync(OUTPUT,{recursive:true});
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
  assert.equal(await p.evaluate(()=>new Set(D.formations.flatMap(f=>f.e.map(e=>e.ac))).size),1);
 }
 for(const [slug,city,lat,lon] of cases) {
  console.log('Test '+slug);
  const {c,p,requests}=await context({geolocation:{latitude:lat,longitude:lon},permissions:['geolocation']});
  await c.addInitScript(()=>localStorage.setItem('stages.academie','paris'));
  await p.goto(BASE+'/apres-3e/'+slug+'/');await loaded(p,slug);
  assert.equal(await p.evaluate(()=>localStorage.getItem('stages.academie')),slug);
  assert(!requests.some(u=>/\/apres-3e\/(apres3e\.json|data\/(creteil|paris|versailles)\.json)/.test(u)),'pas de téléchargement IDF en national');
  assert(!requests.some(u=>u.includes('departements.json')),'pas de contours avant clic');
  assert(!requests.some(u=>u.includes('api-adresse')),'pas de BAN avant saisie');
  await p.locator('[data-k="tout"]').click();
  assert(new URL(p.url()).pathname.endsWith('/'+slug+'/'),'le hash ne perd pas le chemin');
  assert.equal(new URL(p.url()).hash,'#tout');
  assert.equal(requests.filter(u=>/\/data\/[^/]+\.json/.test(u)).length,1,'un seul fichier académie');
  await p.locator('#dCol').click();await p.locator('#col').fill(city);
  await p.locator('#csug button').first().click();
  assert(await p.evaluate(()=>dep!==null),'collège choisi');
  if(slug!=='la-reunion'){
   const b=p.locator('#fdep button').first(),d=await b.getAttribute('data-departement');
   await b.click();assert(await p.evaluate(d=>formations().every(f=>lieux(f).every(x=>x.e.dep!==d)),d));
   await b.click();
  }else assert(await p.locator('#fdep').isHidden());
  await p.locator('#list button[data-i]').first().click();assert(await p.locator('.lieux').count()>0);
  for(const href of await p.locator('.lieux a[data-s="fiche"]').evaluateAll(els=>els.map(e=>e.href)))assert.equal(new URL(href).hostname,'www.onisep.fr');
  const pressure=await p.locator('.lieux').first().innerText();assert(!pressure.includes('premier vœu'));
  if(slug==='lyon'){
   await p.locator('#vC').click();await p.waitForFunction(()=>map&&layer&&layer.getLayers().length>1);
   assert(await p.locator('#map').isVisible());await p.locator('#vL').click();
  }

  await p.locator('.ac-bar button').click();await p.locator('.ac-geo').click();await loaded(p,slug);
  assert(requests.some(u=>u.includes('departements.json')));
  assert(!requests.some(u=>u.includes('api-adresse')),'géolocalisation sans requête BAN');
  await p.locator('.ac-bar button').click();
  await p.locator('#ac-ville').fill(slug==='la-reunion'?'Saint-Denis 97400':city);
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
  if(slug==='lyon'){await p.locator('[data-k=\"cuisine\"]').click();await p.locator('#list button[data-i]').first().click();await p.locator('#s3').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(OUTPUT,'formations-lyon.png')});await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:path.join(OUTPUT,'academie-lyon.png')});}
  const domains=[...new Set(requests.map(u=>new URL(u).hostname))];
  assert(domains.every(d=>['127.0.0.1','localhost','cdnjs.cloudflare.com','api-adresse.data.gouv.fr'].includes(d)||/^[abc]\.tile\.openstreetmap\.org$/.test(d)),domains.join(','));
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
  await p.goto(BASE+'/apres-3e/france/');await p.locator('.ac-geo').click();
  await p.waitForFunction(()=>document.activeElement.id==='ac-ville');
  assert((await p.locator('.ac-status').innerText()).includes('Tape ta ville'));
  await p.screenshot({path:path.join(OUTPUT,'localisation-refusee.png')});
  await p.locator('summary').filter({hasText:'Je connais mon académie'}).click();
  await p.locator('.ac-options button').filter({hasText:'Lyon'}).click();await loaded(p,'lyon');
  await p.reload();await loaded(p,'lyon');await c.close();report.push('Stockage interdit et GPS refusé : repli ville, choix manuel et rechargement du lien OK');
 }
 // Mémoire commune au point d'entrée national ; root historique l'ignore et ne charge pas le module.
 {
  const {c,p,requests}=await context();await p.goto(BASE+'/apres-3e/france/');await p.locator('.ac-picker').waitFor();
  await p.waitForFunction(()=>document.querySelectorAll('.ac-options button').length===30);
  await p.screenshot({path:path.join(OUTPUT,'question.png')});
  await p.evaluate(()=>localStorage.setItem('stages.academie','lille'));
  await p.reload();await loaded(p,'lille');
  requests.length=0;await p.goto(BASE+'/apres-3e/#cuisine');await p.waitForFunction(()=>typeof D!=='undefined'&&D!==null);
  assert.equal(await p.locator('.ac-picker').count(),0);assert.equal(await p.locator('#fdep .chip').count(),3);
  assert(!requests.some(u=>u.includes('/commun/')&&!/\/commun\/accessibilite\.(css|js)$/.test(u)));assert(await p.locator('.lead').innerText().then(s=>s.includes('Île-de-France')));
  await p.screenshot({path:path.join(OUTPUT,'idf-cuisine.png')});
  await p.goto(BASE+'/apres-3e/');await p.waitForFunction(()=>typeof D!=='undefined'&&D!==null);await p.screenshot({path:path.join(OUTPUT,'idf.png')});
  await c.close();report.push('Mémoire commune, entrée France, Île-de-France et #cuisine : OK, aucun module commun/ (hors accessibilité) chargé sur /apres-3e/');
 }
 // Tous les liens d'académie, dont Créteil qui seul doit porter les pressions.
 {
  const {c,p}=await context();
  const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../../commun/academies.json')));
  for(const ac of catalog){
   await p.goto(BASE+'/apres-3e/'+ac.slug+'/#cuisine');await loaded(p,ac.slug);
   assert(await p.locator('#res').isVisible());
   const pressures=await p.evaluate(()=>D.formations.flatMap(f=>f.e).filter(e=>e.p).length);
   assert.equal(pressures>0,ac.slug==='creteil');
   assert((await p.locator('.note').innerText()).includes('dans ton académie'));
  }
  await c.close();report.push('30 liens directs avec #cuisine, filtre et données propres à chaque académie : OK');
 }
 // Erreur de données : pas de résultats d'une ancienne académie, puis nouvelle tentative.
 {
  const {c,p}=await context({expectedFailure:true});
  await c.route('**/data/lyon.json*',r=>r.fulfill({status:503,body:'Indisponible'}));
  await p.goto(BASE+'/apres-3e/lyon/');
  await p.waitForFunction(()=>document.querySelector('.ac-status')?.textContent.includes('réessayer'));
  assert(await p.locator('#nationalContent').isHidden());
  await c.unroute('**/data/lyon.json*');
  await p.locator('summary').click();await p.locator('.ac-options button').filter({hasText:'Lyon'}).click();await loaded(p,'lyon');
  await c.close();report.push('Données indisponibles : message et nouvelle tentative OK');
 }
 assert.deepEqual(allErrors,[],'console sans erreur');
 await browser.close();fs.writeFileSync(path.join(OUTPUT,'resultat.txt'),report.join('\n')+'\nConsole : aucune erreur.\n');console.log(report.join('\n'));console.log('Console : aucune erreur.');
})().catch(e=>{console.error(e);process.exit(1);});
