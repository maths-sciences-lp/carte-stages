/* Même interface et mêmes correspondances ; fichiers département/secteur à la demande. */
import {initAcademie,academieDepuisAdresse,chargerAcademies} from '../commun/academie.js';
import {json,secteur,alternance} from './donnees.js';
const main=$('contenu-principal'),lead=main.querySelector('.lead');
const mount=document.createElement('div');mount.className='stage-academie';main.querySelector('.top').after(mount);
const contenu=document.createElement('div');contenu.id='nationalContent';contenu.hidden=true;
main.append(contenu);contenu.append(lead,$('s1'),$('s2'),$('s3'),$('list'));
const style=document.createElement('style');style.textContent=`#nationalContent .step.off{opacity:1}.stage-academie{padding:0 12px}#nationalContent .lead,#nationalContent .step,#map{visibility:visible}body.stage-question #map,body.stage-question .map-alternative{display:none!important}body.stage-question #panel{width:min(100%,620px);margin:auto;border:0}.stage-note{padding:0 16px;font-size:15px}#stage-retry{margin:8px 12px}`;document.head.append(style);
const carteNote=document.createElement('p');carteNote.className='stage-note';carteNote.id='stage-map-note';carteNote.hidden=true;carteNote.textContent='La carte montre les 1 500 premiers résultats. Tous les résultats restent disponibles dans la liste.';$('s3').append(carteNote);
const retry=document.createElement('button');retry.id='stage-retry';retry.className='btn light';retry.textContent='Réessayer le chargement';retry.hidden=true;$('s3').append(retry);
let catalogue,active,regionDeps=[],request=0,selectionSignal,loadedSignature='',loadingSignature='',timerLoad,failedSignature='';
const schools=new Map();
function memo(cache,key,callback){if(!cache.has(key))cache.set(key,callback().catch(e=>{cache.delete(key);throw e;}));return cache.get(key);}
function departementsUtiles(){
 const o=origin();if(!o)return [];
 if(!dist)return regionDeps;
 const dy=dist/110,dx=dist/(110*Math.max(.1,Math.cos(o.la*Math.PI/180)));
 // Les départements voisins restent disponibles même à une frontière régionale.
 return Object.keys(catalogue.departements).filter(d=>{const b=catalogue.departements[d].bbox;return b[0]<=o.lo+dx&&b[2]>=o.lo-dx&&b[1]<=o.la+dy&&b[3]>=o.la-dy;});
}
function signature(){const o=origin();return JSON.stringify([active?.slug,sel?.type==='f'?sel.x.k:sel?.i,dist,o?.la,o?.lo]);}
loadSec=async k=>{
 if(!origin())return [];
 const deps=departementsUtiles(),meta=await alternance();
 const rows=await Promise.all(deps.map(dep=>secteur(catalogue,dep,k,meta)));
 const o=origin();return rows.flat().filter(r=>!dist||dk({la:r[3],lo:r[4]},o)<=dist).map(r=>mkP(r,k));
};
const legacyRender=render;
render=function(loading){
 if(!active||!catalogue)return;
 if(sel&&origin()&&!loading){
  const sig=signature();
  if(sig!==loadedSignature){
   cl.clearLayers();
   if(sig!==loadingSignature&&sig!==failedSignature){clearTimeout(timerLoad);timerLoad=setTimeout(()=>chargerResultats(sig),0);}
   legacyRender(true);$('count').textContent=failedSignature===sig?'Chargement impossible. Les résultats précédents ne sont pas affichés.':'Chargement des entreprises proches…';return;
  }
 }
 legacyRender(loading);
 if(sel&&!origin()){$('count').textContent='Choisis ton point de départ pour trouver les entreprises proches.';$('list').replaceChildren();}
 carteNote.hidden=P.filter(p=>on.has(p.f)).length<=1500;
};
async function chargerResultats(sig=signature()){
 if(!sel||!origin())return;
 const seq=++request,choice=sel;loadingSignature=sig;failedSignature='';retry.hidden=true;
 try{
  const keys=choice.type==='f'?choice.x.s:IDX.domaines[choice.i].s.map(s=>s.k);
  const parts=await Promise.all(keys.map(loadSec));
  if(seq!==request||sig!==signature()||selectionSignal?.aborted)return;
  const seen=new Set();P=parts.flat().filter(p=>!seen.has(p.s)&&seen.add(p.s));loadedSignature=sig;loadingSignature='';render();
 }catch(e){if(seq!==request||sig!==signature())return;loadingSignature='';failedSignature=sig;P=[];cl.clearLayers();retry.hidden=false;render();}
}
retry.onclick=()=>{failedSignature='';chargerResultats();};
// choose() conserve les champs/boutons/hashes historiques ; le chargement
// national n'a qu'un responsable pour éviter des résultats concurrents.
const legacyChoose=choose;
choose=async c=>{
 loadedSignature='';failedSignature='';++request;await legacyChoose(c);
 if(sel!==c)return;
 if(window.innerWidth<=900)$('s2').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
 if(origin())await chargerResultats();else render();
};
searchAdr=async v=>{
 const response=await fetch('https://api-adresse.data.gouv.fr/search/?autocomplete=1&limit=15&q='+encodeURIComponent(v));
 if(!response.ok)throw Error('Recherche indisponible');
 return((await response.json()).features||[]).filter(f=>academieDepuisAdresse(f)?.region===active?.region).slice(0,5);
};
// Recrée l'écoute de saisie pour écarter une réponse d'une académie précédente.
const address=$('adr').cloneNode(true);$('adr').replaceWith(address);let addressSeq=0,addressTimer;
const pickAddress=f=>{address.value=f.properties.label;setMaison(f.geometry.coordinates[1],f.geometry.coordinates[0],f.properties.label);};
async function chercherAdresse(){const seq=++addressSeq,slug=active?.slug,v=address.value.trim();$('asug').hidden=true;if(v.length<3)return;
 try{const rows=await searchAdr(v);if(seq!==addressSeq||slug!==active?.slug)return;showSug($('asug'),rows,f=>esc(f.properties.label),pickAddress);if(!rows.length)$('amsg').textContent='Adresse non trouvée dans ta région. Essaie une autre ville ou change d’académie.';}
 catch(e){if(seq===addressSeq)$('amsg').textContent='La recherche ne répond pas. Réessaie dans un instant.';}}
address.addEventListener('input',()=>{++addressSeq;clearTimeout(addressTimer);$('asug').hidden=true;addressTimer=setTimeout(chercherAdresse,300);});
address.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();const b=$('asug').querySelector('button');if(b&&!$('asug').hidden)b.click();else chercherAdresse();}});
// La position précise reste en mémoire de la page nationale, sans stockage.
setMaison=(la,lo,label)=>{if(!active)return;pts.maison={la,lo,label};placeMk('maison');from='maison';syncFrom();$('amsg').textContent='✅ '+label;shown=40;render();map.setView([la,lo],13);};
const francais=s=>s.replace(/ ([?!:;])/g,'\u00a0$1');
const walker=document.createTreeWalker(main,NodeFilter.SHOW_TEXT);while(walker.nextNode())walker.currentNode.textContent=francais(walker.currentNode.textContent);
$('dists').querySelector('[data-d="0"]').textContent='Toute la région';
const footer=document.querySelector('footer');
for(const node of [...footer.childNodes])if(node.nodeType===3)node.textContent=node.textContent.replace(/\), \d{1,2} [a-zéû]+ \d{4}, /u,'), ');
const sourceDate=document.createElement('p');sourceDate.id='stage-source-date';footer.prepend(sourceDate);
const sourceSchools=document.createElement('p');sourceSchools.textContent='Lycées proposant une voie professionnelle : annuaire de l’Éducation nationale et Onisep. Les entreprises proposées correspondent à des types d’activité ; vérifie avec ton professeur les activités possibles pour ton stage.';footer.append(sourceSchools);
const syncQuestion=()=>{document.body.classList.toggle('stage-question',contenu.hidden);if(contenu.hidden){++request;++addressSeq;clearTimeout(timerLoad);cl.clearLayers();}else setTimeout(()=>map.invalidateSize(),0);};
new MutationObserver(syncQuestion).observe(contenu,{attributes:true,attributeFilter:['hidden']});syncQuestion();
await chargerAcademies();
await initAcademie({mount,contenu,baseOutil:new URL('stage/',document.baseURI),onSelect:async(ac,{signal})=>{
 const data=catalogue||await json('catalogue-leger.json',{signal});
 if(data.schema!==1||!data.academies.some(a=>a.slug===ac.slug))throw Error('Académie indisponible');
 const deps=data.academies.filter(a=>a.region===ac.region).flatMap(a=>a.deps);
 const lists=await Promise.all(deps.map(dep=>memo(schools,data.version+'/'+dep,()=>json('lycees/'+dep+'.json',{version:data.departements[dep].lycees.sha256}))));
 if(signal.aborted)return;
 ++request;++addressSeq;clearTimeout(timerLoad);selectionSignal=signal;active=ac;catalogue=data;regionDeps=deps;
 loadedSignature='';loadingSignature='';failedSignature='';retry.hidden=true;P=[];sel=null;booted=false;on.clear();cl.clearLayers();ring.remove();
 for(const key of ['maison','lycee']){pts[key]=null;if(mks[key]){mks[key].remove();delete mks[key];}}
 Object.keys(LBAC).forEach(k=>delete LBAC[k]);LBA=null;$('lba-source').hidden=true;
 LY=lists.flat();LY.forEach(l=>l.key=norm(l.n+' '+l.c+' '+l.p));
 $('adr').value='';$('lyc').value='';$('f').value='';$('chosen').hidden=true;$('pick').hidden=false;
 ['amsg','lmsg'].forEach(k=>$(k).textContent='');['fsug','asug','lsug'].forEach(k=>$(k).hidden=true);
 from='maison';shown=40;dist=5;document.querySelectorAll('#dists .chip').forEach(b=>b.setAttribute('aria-pressed',b.dataset.d==='5'));
 lead.textContent='Trouve des entreprises près de chez toi — '+ac.region+'.';document.title='Trouve ton stage – '+ac.nom;
 document.querySelector('meta[name="description"]').content=lead.textContent;
 sourceDate.textContent='Données préparées le '+new Date(data.date+'T12:00:00').toLocaleDateString('fr-FR')+'.';
 const bounds=deps.map(d=>data.departements[d].bbox);map.fitBounds([[Math.min(...bounds.map(b=>b[1])),Math.min(...bounds.map(b=>b[0]))],[Math.max(...bounds.map(b=>b[3])),Math.max(...bounds.map(b=>b[2]))]]);
 demarrer(data);initLycee();

}});
