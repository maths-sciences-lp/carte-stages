/* Régressions du départ des trajets, hors réseau : node --test formation/tests/depart.cjs */
const assert=require('node:assert/strict');
const {test}=require('node:test');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const application=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]).find(x=>x.includes('function origine()'));
const fixture={henaff:'lycee',classes:[],region:'Région test',dip:{d:{lib:'Bac pro test',ly:['lycee'],s:['bts'],a:[]}},lycees:{lycee:{n:'Lycée test',v:'Ville',lat:48.9,lon:2.4}},suites:{bts:{n:'BTS test',o:'formation.1',e:[{n:'Lieu test',v:'Ville',a:'1 rue Test',cp:'75000',lat:48.9,lon:2.4,st:'public',o:'https://www.onisep.fr/lieu'}]}}};

function app(){
 const nodes=new Map();
 class Element{
  constructor(id=''){this.id=id;this.value='';this.hidden=false;this.textContent='';this.innerHTML='';this.style={};this.events={};this.attributes={};}
  setAttribute(k,v){this.attributes[k]=String(v);}
  addEventListener(k,fn){this.events[k]=fn;}
  querySelector(q){return element(q);}
  querySelectorAll(){return [];}
  append(){} appendChild(){} after(){} before(){} insertBefore(){} replaceChildren(){} focus(){}
  cloneNode(){return Object.assign(new Element(this.id),{value:this.value});}
  replaceWith(e){nodes.set(this.id,e);}
 }
 const element=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);};
 element('.ou').nextElementSibling=element('heading');element('heading').nextElementSibling=element('academyHint');
 let academySelection;
 const context=vm.createContext({
  document:{getElementById:element,querySelector:element,createElement:()=>new Element(),createTreeWalker:()=>({nextNode:()=>false}),baseURI:'http://localhost/formation/'},
  window:{FORMATION_NATIONAL:true,addEventListener(){}},location:{hostname:'localhost',protocol:'http:',pathname:'/formation/',search:'',hash:''},
  navigator:{},history:{replaceState(){}},URL,URLSearchParams,NodeFilter:{SHOW_TEXT:4},
  setTimeout(){return 1;},clearTimeout(){},
  fetch:async url=>({ok:true,json:async()=>String(url).includes('-parcoursup')?{f:{}}:structuredClone(fixture)}),
  initAcademie:async options=>{academySelection=options.onSelect;},academieDepuisAdresse:()=>({slug:'test'})
 });
 const run=code=>vm.runInContext(code,context);
 run(application);run(`D=${JSON.stringify(fixture)};cur={d:'d',ly:'lycee'};draw();`);
 return {run,element,context,national:async()=>{
  const source=fs.readFileSync(path.join(root,'national.js'),'utf8').replace(/^import .*;$/m,'');
  await run('(async()=>{'+source+'})()');
  await academySelection({slug:'test',nom:'Académie test'},{signal:{aborted:false}});
  run("cur={d:'d',ly:'lycee'};draw();");
 },changeAcademy:()=>academySelection({slug:'autre',nom:'Autre académie'},{signal:{aborted:false}})};
}
function chooseHome(a){a.run("depart(true);$('adr').value='Adresse choisie';setMaison(48.85,2.35,'Adresse choisie');");}
function origin(a){return JSON.parse(a.run('JSON.stringify(origine())'));}
function route(a){const url=a.element('list').innerHTML.match(/href="(https:\/\/www\.google\.com\/maps\/dir\/[^\"]+)"/)[1];return new URL(url).searchParams.get('origin');}

for(const national of [false,true]){
 const label=national?'académie':'Île-de-France';
 test(label+' : domicile → lycée → domicile conserve adresse, distance et itinéraire',async()=>{
  const a=app();if(national)await a.national();chooseHome(a);
  const homeHtml=a.element('list').innerHTML,homeDistance=a.run('lignes()[0].d');
  assert.equal(route(a),'48.85,2.35');assert(homeDistance>0);
  a.run('depart(false)');assert.equal(route(a),'48.9,2.4');assert.equal(a.run('lignes()[0].d'),0);
  assert.match(a.element('list').innerHTML,/Ton lycée/);
  a.run('depart(true)');assert.deepEqual(origin(a),{lat:48.85,lon:2.35,n:'Adresse choisie'});
  assert.equal(a.element('adr').value,'Adresse choisie');assert.match(a.element('amsg').textContent,/chez toi/);
  assert.equal(a.run('lignes()[0].d'),homeDistance);assert.equal(a.element('list').innerHTML,homeHtml);
  assert.equal(a.element('dMai').attributes['aria-pressed'],'true');assert.equal(a.element('dLyc').attributes['aria-pressed'],'false');
 });
 test(label+' : domicile sans adresse ne reprend pas silencieusement le lycée',async()=>{
  const a=app();if(national)await a.national();a.run('depart(true)');
  assert.equal(origin(a),null);assert.equal(a.run('lignes()[0].d'),null);assert.equal(route(a),null);
  assert.match(a.element('list').innerHTML,/Choisis ton adresse/);
 });
 test(label+' : modifier ou effacer l’adresse invalide les anciennes coordonnées',async()=>{
  const a=app();if(national)await a.national();chooseHome(a);
  a.element('adr').value='Nouvelle adresse';a.element('adr').events.input();
  assert.equal(origin(a),null);assert.equal(route(a),null);assert.equal(a.element('amsg').textContent,'');
  a.run("setMaison(48.8,2.3,'Nouvelle adresse')");assert.equal(route(a),'48.8,2.3');
  a.element('adr').value='';a.element('adr').events.input();assert.equal(origin(a),null);
  a.run('depart(false)');assert.equal(route(a),'48.9,2.4');
 });
}
test('une localisation arrivée après un changement de mode ne remplace pas le départ lycée',()=>{
 const a=app();a.context.navigator.geolocation={getCurrentPosition:ok=>{a.gps=ok;}};
 a.run('depart(true)');a.element('geo').onclick();a.run('depart(false)');
 a.gps({coords:{latitude:48.85,longitude:2.35}});assert.equal(route(a),'48.9,2.4');
 a.run('depart(true)');assert.equal(route(a),'48.85,2.35');
});
test('changer d’académie efface le domicile mémorisé',async()=>{
 const a=app();await a.national();chooseHome(a);await a.changeAcademy();
 a.run("cur={d:'d',ly:'lycee'};depart(true)");
 assert.equal(origin(a),null);assert.equal(route(a),null);assert.equal(a.element('adr').value,'');
});
