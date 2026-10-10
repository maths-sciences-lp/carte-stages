/* Parcours effectués par Tab, Entrée, Espace et flèches ; aucune activation par clic. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),assert=require('assert');
(async()=>{const b=await chromium.launch(),p=await b.newPage({viewport:{width:375,height:812}}),rows=[];p.on('pageerror',e=>{throw e});
const base=process.env.BASE_URL||'http://127.0.0.1:8768';
async function tabTo(selector){for(let i=0;i<250;i++){if(await p.evaluate(s=>document.activeElement.matches(s),selector))return;await p.keyboard.press(await p.evaluate(s=>document.activeElement.compareDocumentPosition(document.querySelector(s))&2?'Shift+Tab':'Tab',selector));}throw Error('Inatteignable par Tab : '+selector);}
async function enter(selector){await tabTo(selector);await p.keyboard.press('Enter');await p.waitForTimeout(80);}
async function check(selector,action){assert(await p.evaluate(s=>document.activeElement.matches(s),selector),action+': focus perdu '+await p.evaluate(()=>document.activeElement.outerHTML.slice(0,220)));rows.push({action,focus:selector});}
await p.goto(base+'/');await p.waitForFunction(()=>booted);await p.keyboard.press('Escape');await tabTo('#f');await p.keyboard.type('cuisine');await p.keyboard.press('ArrowDown');await p.keyboard.press('Enter');await p.waitForTimeout(200);await check('#change','Stage : sélectionner une formation');
await enter('[data-from="lycee"]');await tabTo('#lyc');await p.keyboard.type('Paris');await p.keyboard.press('ArrowDown');await p.keyboard.press('Enter');await p.waitForTimeout(200);await check('#lyc','Stage : sélectionner un lycée');await enter('#tc');await enter('#tl');rows.push({action:'Stage : Liste → Carte → Liste'});
for(const tool of ['apres-3e','formation','aide']){
 await p.goto(base+'/'+tool+'/'+(tool==='formation'?'#era':''));await p.waitForFunction(()=>D);const choice=tool==='formation'?'#classes button':'#doms button';await enter(choice);await check(choice,tool+': choix principal');
 if(tool==='apres-3e'){await enter('#list button[data-i]');await check('#list button[data-i]',tool+': ouvrir les lycées');assert.equal(await p.locator('#list button[data-i]').first().getAttribute('aria-expanded'),'true');}
 if(tool!=='formation'){if(tool==='aide')await enter('#dCol');await tabTo('#col');await p.keyboard.type('Paris');await p.keyboard.press('ArrowDown');await p.keyboard.press('Enter');await p.waitForTimeout(80);await check('#col',tool+': collège');}
 await enter('#vC');await enter('#vL');rows.push({action:tool+': Liste → Carte → Liste'});
 await p.evaluate(()=>localStorage.removeItem('stages.academie'));await p.goto(base+'/'+tool+'/france/');await p.locator('.ac-picker').waitFor();await enter('.ac-picker summary');await enter('.ac-options button:nth-child(16)');await p.waitForFunction(()=>!document.querySelector('#nationalContent').hidden);await check('#nationalContent h2',tool+': académie choisie');await enter('.ac-bar button');await check('#ac-title',tool+': changer');
}
await p.goto(base+'/demo/');await enter('.transcription summary');assert(await p.locator('.transcription').first().getAttribute('open')!==null);rows.push({action:'Demo : ouvrir la transcription au clavier'});
fs.writeFileSync(process.env.OUTPUT||'/tmp/rgaa-clavier.json',JSON.stringify(rows,null,2));console.log(rows);await b.close();})().catch(e=>{console.error(e);process.exit(1)});
