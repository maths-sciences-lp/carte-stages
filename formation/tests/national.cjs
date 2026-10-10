/* Navigateur réel à 375 px. GPS simulé, BAN (réponses enregistrées, tests/ban-fixture.cjs) après saisie uniquement. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const ban=require('../../tests/ban-fixture.cjs');
const BASE=process.env.BASE_URL||'http://127.0.0.1:8767';
const OUTPUT=process.env.TEST_OUTPUT||'/tmp/formation-national';fs.mkdirSync(OUTPUT,{recursive:true});
const cases=[['lyon','Lyon',45.764,4.8357],['lille','Lille',50.6292,3.0573],['aix-marseille','Marseille',43.2965,5.3698],['rennes','Rennes',48.1173,-1.6778],['la-reunion','Saint-Denis',-20.8823,55.4504]];
(async()=>{
 const browser=await chromium.launch();const errors=[],report=[];
 async function context(options={}){const c=await browser.newContext({viewport:{width:375,height:812},...options});await ban.brancher(c);const p=await c.newPage(),requests=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});p.on('request',r=>requests.push(r.url()));return {c,p,requests};}
 async function loaded(p,slug){await p.waitForFunction(s=>location.pathname.endsWith('/'+s+'/')&&typeof D!=='undefined'&&D!==null&&!document.querySelector('#nationalContent').hidden,slug);assert(!(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));assert(await p.locator('.ac-bar').isVisible());}
 async function choice(p){const d=await p.evaluate(()=>Object.entries(D.dip).find(([id,x])=>x.s.length&&x.ly.length>1));assert(d);await p.locator('#q').fill(d[1].lib);await p.locator('#qsug button').filter({hasText:d[1].lib}).first().click();await p.locator('#ly').selectOption(d[1].ly[0]);assert(await p.locator('#list .it').count()>0);assert.equal(await p.evaluate(()=>cur.ly),d[1].ly[0]);assert(new URL(p.url()).hash.includes('&ly='));for(const href of await p.locator('a[data-s="fiche"]').evaluateAll(a=>a.map(x=>x.href)))assert.equal(new URL(href).hostname,'www.onisep.fr');return d;}
 for(const [slug,city,lat,lon] of cases){
  console.log('Test '+slug);const {c,p,requests}=await context({geolocation:{latitude:lat,longitude:lon},permissions:['geolocation']});await c.addInitScript(()=>localStorage.setItem('stages.academie','paris'));
  await p.goto(BASE+'/formation/'+slug+'/');await loaded(p,slug);assert.equal(await p.evaluate(()=>localStorage.getItem('stages.academie')),slug);
  assert(!requests.some(u=>/\/formation\/(formations|parcoursup)\.json/.test(u)));assert(!requests.some(u=>u.includes('api-adresse')||u.includes('departements.json')));
  assert.equal(requests.filter(u=>/\/data\/[^/]+\.json/.test(u)).length,2);await choice(p);await p.reload();await loaded(p,slug);assert(await p.locator('#list .it').count()>0);
  if(slug==='lyon'){await p.locator('#s3').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(OUTPUT,'poursuites-lyon.png')});await p.locator('#vC').click();await p.waitForFunction(()=>map&&layer&&layer.getLayers().length>1);await p.locator('#vL').click();}
  await p.locator('.ac-bar button').click();await p.locator('.ac-geo').click();await loaded(p,slug);assert(requests.some(u=>u.includes('departements.json')));assert(!requests.some(u=>u.includes('api-adresse')));await choice(p);
  await p.locator('.ac-bar button').click();await p.locator('#ac-ville').fill(slug==='la-reunion'?'Saint-Denis 97400':city);await p.locator('.ac-suggestions button').first().waitFor();
  const suggestions=p.locator('.ac-suggestions button');let picked=false;for(let i=0;i<await suggestions.count();i++){if(slug!=='la-reunion'||/97400|Réunion/.test(await suggestions.nth(i).innerText())){await suggestions.nth(i).click();picked=true;break;}}assert(picked);await loaded(p,slug);await choice(p);
  await p.locator('.ac-bar button').click();await p.locator('summary').filter({hasText:'Je connais mon académie'}).click();await p.locator('.ac-options button').filter({hasText:slug==='la-reunion'?'La Réunion':slug==='aix-marseille'?'Aix-Marseille':city}).click();await loaded(p,slug);await choice(p);
  const hosts=[...new Set(requests.map(u=>new URL(u).hostname))];assert(hosts.every(d=>['127.0.0.1','api-adresse.data.gouv.fr'].includes(d)||/^[abc]\.tile\.openstreetmap\.org$/.test(d)),hosts.join(','));
  report.push(slug+' : adresse directe, GPS simulé, ville BAN (réponse enregistrée), changer ; diplôme, lycée et poursuites vérifiés après chaque choix ; URL et rechargement OK');await c.close();
 }
 {
  const {c,p,requests}=await context();await p.goto(BASE+'/formation/france/');await p.waitForFunction(()=>document.querySelectorAll('.ac-options button').length===30);await p.screenshot({path:path.join(OUTPUT,'question.png')});await p.evaluate(()=>localStorage.setItem('stages.academie','lille'));await p.reload();await loaded(p,'lille');
  requests.length=0;await p.goto(BASE+'/formation/');await p.waitForFunction(()=>D&&PS);assert.equal(await p.locator('.ac-picker').count(),0);assert(!requests.some(u=>u.includes('/commun/')&&!/\/commun\/(accessibilite\.(css|js)|navigation\.(css|js)|pied\.js|academie\.js|icones\.svg|logo\.svg|leaflet\/[^/]+(\/[^/]+)?)$/.test(u)));assert(!await p.locator('.hen').isVisible(),'raccourcis Hénaff masqués sans contexte');await p.goto(BASE+'/formation/#era');await p.waitForFunction(()=>D&&PS);assert(await p.locator('.hen').isVisible(),'raccourcis Hénaff avec un lien de classe');await p.screenshot({path:path.join(OUTPUT,'idf.png')});
  for(const k of ['eeb','iccer','mee','tma','era','geometre','mit','sdg','ebeniste','bma-ebeniste','bma-signaletique']){await p.goto(BASE+'/formation/#'+k);await p.waitForFunction(k=>D&&PS&&cur?.k===k,k);assert(await p.locator('#res').isVisible());assert((await p.locator('main section').first().innerText()).includes('Hénaff'));if(k==='eeb'){await p.screenshot({path:path.join(OUTPUT,'idf-eeb.png')});await p.locator('#s3').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(OUTPUT,'idf-eeb-poursuites.png')});}}
  await c.close();report.push('Entrée France et mémoire commune ; /formation/ sans sélecteur ; 11 liens Hénaff : OK');
 }
 {
  const {c,p}=await context();const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../../commun/academies.json')));for(const ac of catalog){await p.goto(BASE+'/formation/'+ac.slug+'/');await loaded(p,ac.slug);assert.equal(await p.evaluate(()=>D.academie),ac.nom);assert.equal(await p.locator('.hen').isVisible(),false);await choice(p);}await c.close();report.push('30 adresses directes : académie, diplôme, lycée, poursuites et absence de débordement horizontal OK');
 }
 {
  const {c,p}=await context();await c.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new DOMException('indisponible','SecurityError');}});Object.defineProperty(navigator,'geolocation',{value:{getCurrentPosition(ok,fail){fail({code:1});}}});});await p.goto(BASE+'/formation/france/');await p.locator('.ac-geo').click();await p.waitForFunction(()=>document.activeElement.id==='ac-ville');await p.locator('summary').filter({hasText:'Je connais mon académie'}).click();await p.locator('.ac-options button').filter({hasText:'Lyon'}).click();await loaded(p,'lyon');await c.close();report.push('Stockage bloqué et GPS refusé : repli ville/choix manuel OK');
 }
 assert.deepEqual(errors,[]);ban.verifier();await browser.close();report.push('375 px ; console : aucune erreur.');fs.writeFileSync(path.join(OUTPUT,'resultat.txt'),report.join('\n')+'\n');console.log(report.join('\n'));
})().catch(e=>{console.error(e);process.exit(1);});
