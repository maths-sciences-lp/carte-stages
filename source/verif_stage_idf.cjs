/* Contrat des liens historiques et mesures navigateur de la migration 8.5. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{execFileSync}=require('child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const old=read(path.join(cfg.root,'data/index.json')),schools=read(path.join(cfg.root,'data/lycees.json'));
const aliases=read(path.join(cfg.root,'stage/aliases-idf.json')),cat=read(path.join(cfg.data,'catalogue.json'));
const short=['tne','mnb','mama','iccer','mee','tma','era','eeb','geometre','mit','sdg','ebeniste','bma-ebeniste','bma-signaletique','ma'];
const extra=['cap-cuisine','cap-boulanger','cap-patissier','cap-accompagnant-educatif-petite-enfance','bac-pro-accompagnement-soins-et-services-a-la-personne'];
const historic=new Map();for(const f of old.formations)if(!historic.has(f.k))historic.set(f.k,f);
for(const [k,f] of historic){const n=cat.formations.find(n=>n.k===(aliases[k]||k));assert(n,k);assert.deepEqual(n.s,f.s,k);assert.equal(n.n,f.n,k);}
assert.equal(historic.size,180);assert.equal(schools.length,469);
const report={cles:historic.size,lycees:schools.length,adresses:[],mesures:[],frontieres:[],erreurs:[]};
(async()=>{
 const browser=await chromium.launch();
 async function context(width=375){const c=await browser.newContext({viewport:{width,height:812}});
  await c.addInitScript(()=>{try{localStorage.setItem('stages.vu','1');}catch(e){}});
  await c.route(/goatcounter|gc\.zgo\.at/,r=>r.fulfill({status:204,body:''}));
  await c.route('https://maths-sciences-lp.github.io/carte-stages-donnees/**',async r=>{
   const rel=new URL(r.request().url()).pathname.split('/carte-stages-donnees/')[1];const p=path.resolve(cfg.data,rel);
   assert(p.startsWith(path.resolve(cfg.data)+path.sep));await r.fulfill({status:fs.existsSync(p)?200:404,body:fs.existsSync(p)?fs.readFileSync(p):'',contentType:'application/json'});
  });return c;
 }
 async function ready(page,selected=false){await page.waitForFunction(()=>typeof IDX!=='undefined'&&IDX&&typeof LY!=='undefined'&&LY.length>0);if(selected)await page.waitForFunction(()=>sel&&/entreprise/.test($('count').textContent)&&!$('count').textContent.startsWith('Chargement'),null,{timeout:60000});}
 for(const width of [375,320]){
  const c=await context(width),page=await c.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  const routes=['/',...short.map(s=>'/'+s),...extra.map(f=>'/#f='+f+'&ly=0932119Y'),...Object.keys(aliases).map(f=>'/#f='+f+'&ly=0932119Y'),'/#d=0&ly=0932119Y','/#f=cap-cuisine&d=2&ly=0932119Y','/#f=cap-cuisine&d=2','/#ly=0932119Y','/#d=2','/#f=cap-cuisine&lycee=48.874884,2.430721'];
  for(const route of routes){await page.goto('about:blank');await page.goto(cfg.local+route,{waitUntil:'domcontentloaded'});const selected=route!=='/'&&!/^\/#ly=/.test(route);await ready(page,selected);
   const s=await page.evaluate(()=>({formation:sel?.type==='f'?sel.x.k:null,domaine:sel?.type==='d'?sel.i:null,lycee:pts.lycee?.u||null,count:$('count').textContent,hash:location.hash,width:document.documentElement.scrollWidth,viewport:innerWidth,question:document.body.innerText.includes('Tu habites où')}));
   assert.equal(s.question,false,route);assert(s.width<=s.viewport,route+' débordement');const h=new URLSearchParams(s.hash.slice(1));
   if(h.has('f'))assert.equal(s.formation,h.get('f'),route);if(h.has('ly'))assert.equal(s.lycee,h.get('ly'),route);if(!h.has('f')&&h.has('d'))assert.equal(s.domaine,+h.get('d'),route);
   report.adresses.push({route,width,...s});
  }
  await page.goto('about:blank');await page.goto(cfg.local+'/');await ready(page);
  const all=await page.evaluate(keys=>keys.every(k=>!!window.resoudreFormationIDF(k,IDX)),[...historic.keys()]);assert(all);
  const uas=await page.evaluate(()=>LY.map(x=>x.u));assert.deepEqual(uas.sort(),schools.map(x=>x.u).sort());
  await page.keyboard.press('Tab');assert(await page.locator('.skip-link').evaluate(e=>e===document.activeElement));await page.keyboard.press('Enter');
  await page.locator('#f').focus();await page.keyboard.type('ICCER');await page.locator('#fsug button').first().waitFor();await page.keyboard.press('Tab');await page.keyboard.press('Enter');await ready(page,true);
  assert(await page.evaluate(()=>!!sel));
  await page.screenshot({path:path.join(cfg.output,'carte-'+width+'.png'),fullPage:false});
  report.erreurs.push(...errors);await c.close();
 }
 // Même départ francilien et un point frontalier Normandie / Hauts-de-France.
 const c=await context(),p=await c.newPage();
 for(const test of [{url:'/iccer',label:'Hénaff vers Paris',dep:'75'},
 {url:'/#f=cap-cuisine',label:'Égreville (Créteil) vers Dordives (Orléans-Tours)',dep:'45',point:[48.157,2.841]},
 {url:'/stage/normandie/#f=cap-cuisine',label:'Eu (Normandie) vers Mers-les-Bains (académie Amiens)',dep:'80',point:[50.049,1.420]}]){
  await p.goto(cfg.local+test.url);await p.waitForFunction(()=>typeof IDX!=='undefined'&&IDX);
  if(test.point)await p.evaluate(([la,lo])=>setMaison(la,lo,'Eu'),test.point);
  await ready(p,true);
  const sectorKeys=await p.evaluate(()=>sel.x.s);
  const target=new Set(sectorKeys.flatMap(k=>read(path.join(cfg.data,'sirene',test.dep,k+'.json')).map(r=>r[7])));
  const visible=await p.evaluate(()=>P.filter(p=>on.has(p.f)&&dk(p,origin())<=5).map(p=>p.s));const cross=visible.filter(s=>target.has(s));assert(cross.length>0,test.label);
  report.frontieres.push({test:test.label,departement:test.dep,entreprises:cross.length,exemples:cross.slice(0,5)});
 }
 await c.close();
 // Conservation du point Maison, stockage refusé, reprise et navigation obsolète.
 {
  const c=await context(),p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(cfg.local+'/');await ready(p);await p.evaluate(()=>setMaison(48.874884,2.430721,'Maison test'));
  await p.reload();await ready(p);assert.equal(await p.evaluate(()=>pts.maison.label),'Maison test');
  await p.evaluate(()=>choose({type:'f',x:IDX.formations.find(f=>f.k==='cap-cuisine')}));await ready(p,true);
  assert(await p.evaluate(()=>P.some(p=>lbaFor(p))),'Badges LBA chargés');
  const axe=process.env.AXE_MODULE||'/tmp/carte-stages-rgaa-tools/node_modules/axe-core/axe.min.js';
  if(fs.existsSync(axe)){await p.addScriptTag({path:axe});const results=await p.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));assert.deepEqual(results.violations.map(v=>v.id),[]);report.axe='aucune violation détectée';}
  await c.close();assert.deepEqual(errors,[]);
 }
 {
  const c=await context(),p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await c.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Refus simulé','SecurityError');}}));
  await p.goto(cfg.local+'/iccer');await ready(p,true);assert.deepEqual(errors,[]);await c.close();
 }
 {
  const c=await context(),p=await c.newPage();let fail=true;
  const matcher='https://maths-sciences-lp.github.io/carte-stages-donnees/sirene/**';
  await c.route(matcher,r=>fail?r.fulfill({status:503,body:'Indisponible'}):r.fallback());
  await p.goto(cfg.local+'/iccer');await p.locator('#idf-retry').waitFor({state:'visible'});assert.equal(await p.evaluate(()=>P.length),0);
  fail=false;await p.locator('#idf-retry').click();await ready(p,true);assert.equal(await p.evaluate(()=>P.filter(p=>dk(p,origin())<=5).length),777);await c.close();
 }
 report.etats='Maison persistante ; stockage refusé ; badges LBA ; reprise HTTP 503 vérifiés';
 // Mesure contrôlée : navigateur 375 px, processeur ralenti x4, fichiers locaux.
 for(const mode of ['avant','apres'])for(const route of ['/','/iccer']){
  const c=await context(),p=await c.newPage(),cdp=await c.newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
  if(mode==='avant'){const html=execFileSync('git',['show','origin/main:index.html'],{cwd:cfg.root});await p.route(cfg.local+'/',r=>r.fulfill({status:200,body:html,contentType:'text/html'}));}
  const t=Date.now();await p.goto(cfg.local+route);await ready(p,route!=='/');
  const resources=await p.evaluate(()=>performance.getEntriesByType('resource').map(r=>r.name));
  assert(!resources.some(u=>/\/catalogue\.json/.test(u)));
  if(route==='/'&&mode==='apres')assert(!resources.some(u=>/\/(sirene|manifestes|lba)\//.test(u)));
  report.mesures.push({mode,route,ms:Date.now()-t,cpu:4,ressources:resources.filter(u=>u.includes('carte-stages-donnees'))});
  if(route==='/iccer'){const t=Date.now();await p.locator('[data-d="0"]').click();await p.waitForFunction(()=>/entreprises$/.test($('count').textContent));report.mesures.push({mode,route:'/iccer : Toute la région (bouton Toutes)',ms:Date.now()-t,cpu:4,count:await p.locator('#count').innerText()});}
  await c.close();
 }
 assert.deepEqual(report.erreurs,[]);await browser.close();fs.writeFileSync(path.join(cfg.output,'carte-contrat.json'),JSON.stringify(report,null,2));console.log(`Carte : ${report.adresses.length} parcours à 320/375 px ; 180 clés ; 469 UAI ; frontières et clavier vérifiés ; aucune erreur.`);
})().catch(e=>{console.error(e);process.exit(1)});
