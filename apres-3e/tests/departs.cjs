/* Départs et suggestions d'adresse (Après le collège, Qui peut m'aider ?), navigateur réel.
   BASE_URL pointe sur python3 -m http.server. Audit du 8/10/2026, points 2 et 5. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const ban=require('../../tests/ban-fixture.cjs');
const BASE=(process.env.BASE_URL||'http://127.0.0.1:8766').replace(/\/$/,'');
(async()=>{const b=await chromium.launch();const err=[];
 async function page(u){const c=await b.newContext({viewport:{width:390,height:844}});await ban.brancher(c);const p=await c.newPage();p.on('pageerror',e=>err.push(e.message));
  await p.route(/goatcounter|gc\.zgo\.at/,r=>r.fulfill({status:204,body:''}));
  await p.goto(BASE+u,{waitUntil:'networkidle'});await p.waitForFunction(()=>typeof D!=='undefined'&&D);return p;}
 // Après le collège : domicile → collège → domicile
 let p=await page('/apres-3e/#tout');
 const d=()=>p.evaluate(()=>JSON.stringify(dep));
 await p.evaluate(()=>{$('dMai').click();setDep(48.8566,2.3524,'de chez toi','maison');});const maison=await d();
 await p.evaluate(()=>{$('dCol').click();setDep(48.8749,2.4307,'du collège test','college');});const college=await d();
 assert.notEqual(maison,college);
 await p.evaluate(()=>$('dMai').click());assert.equal(await d(),maison,'retour chez moi : coordonnées du domicile');
 await p.evaluate(()=>$('dCol').click());assert.equal(await d(),college,'retour au collège : coordonnées du collège');
 // modifier l'adresse efface l'ancien domicile
 await p.evaluate(()=>$('dMai').click());await p.locator('#adr').fill('nouvelle adresse');assert.equal(await d(),'null');
 // une réponse lente n'écrase pas la suivante ; champ effacé = pas de suggestions
 await p.evaluate(()=>{searchAdr=v=>new Promise(r=>setTimeout(()=>r([{properties:{label:'R '+v,postcode:'75001'},geometry:{coordinates:[2.35,48.85]}}]),v==='rue de la'?900:50));});
 await p.locator('#adr').fill('rue de la');await p.waitForTimeout(350);await p.locator('#adr').fill('rue de la paix');await p.waitForTimeout(1200);
 assert.equal(await p.locator('#asug').innerText(),'R rue de la paix');
 await p.locator('#adr').fill('rue du bac');await p.waitForTimeout(300);await p.locator('#adr').fill('');await p.waitForTimeout(1200);
 assert(await p.evaluate(()=>$('asug').hidden),'suggestions cachées après effacement');
 await p.context().close();
 // Qui peut m'aider ? : domicile → lycée → domicile
 p=await page('/aide/#tout');
 await p.evaluate(()=>{$('dMai').click();setDep(48.8566,2.3524,'de chez toi','maison');});const m2=await d();
 await p.evaluate(()=>{$('dLyc').click();setDep(48.8749,2.4307,'du lycée test','lycee');});
 await p.evaluate(()=>$('dMai').click());assert.equal(await d(),m2,'aide : retour chez moi');
 await p.evaluate(()=>$('dCol').click());assert.equal(await d(),'null','aide : collège jamais choisi');
 await p.context().close();await b.close();
 assert.deepEqual(err,[]);ban.verifier();console.log('Départs (collège, lycée, chez moi) et suggestions d’adresse : OK');
})().catch(e=>{console.error(e);process.exit(1);});
