/* Les liens historiques gardent leur identité et leur interface francilienne. */
import {json,secteur,alternance} from './donnees.js';
if(!window.STAGE_NATIONAL){
 window.STAGE_IDF=true;
 const IDF=['75','77','78','91','92','93','94','95'];
 let catalogue,sequence=0,loaded='',loading='',failed='';
 const retry=document.createElement('button');retry.className='btn light';retry.id='idf-retry';retry.hidden=true;retry.textContent='Réessayer le chargement';$('s3').append(retry);
 const signature=()=>JSON.stringify([sel?.type==='f'?sel.x.k:sel?.i,origin()?.la,origin()?.lo,dist]);
 function deps(){
  const o=origin();if(!o||!dist)return IDF;
  const dy=dist/110,dx=dist/(110*Math.max(.1,Math.cos(o.la*Math.PI/180)));
  return Object.keys(catalogue.departements).filter(d=>{const b=catalogue.departements[d].bbox;return b[0]<=o.lo+dx&&b[2]>=o.lo-dx&&b[1]<=o.la+dy&&b[3]>=o.la-dy;});
 }
 loadSec=async k=>{
  const meta=await alternance();
  const rows=await Promise.all(deps().map(d=>secteur(catalogue,d,k,meta)));
  return rows.flat().map(r=>mkP(r,k));
 };
 const previousRender=render;
 render=function(wait){
  if(catalogue&&sel&&!wait&&loaded!==signature()){
   const sig=signature();cl.clearLayers();previousRender(true);
   if(failed===sig){$('count').textContent='Chargement impossible. Vérifie ta connexion puis réessaie.';return;}
   $('count').textContent='Chargement des entreprises…';
   if(loading!==sig)charger();return;
  }
  previousRender(wait);
 };
 async function charger(){
  if(!catalogue||!sel)return;
  const sig=signature(),seq=++sequence;loading=sig;failed='';retry.hidden=true;
  try{
   const keys=sel.type==='f'?sel.x.s:IDX.domaines[sel.i].s.map(s=>s.k);
   const parts=await Promise.all(keys.map(loadSec));
   if(seq!==sequence||sig!==signature())return;
   const seen=new Set();P=parts.flat().filter(p=>!seen.has(p.s)&&seen.add(p.s));
   loaded=sig;loading='';render();
  }catch(e){if(seq!==sequence||sig!==signature())return;failed=sig;loading='';P=[];retry.hidden=false;render();}
 }
 const previousChoose=choose;
 choose=async c=>{++sequence;loaded='';failed='';await previousChoose(c);if(sel===c){await charger();if(window.innerWidth<=900)$('s2').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});}};
 async function init(){
  retry.hidden=true;
  try{
   const [data,aliases]=await Promise.all([json('catalogues/ile-de-france.json'),fetch('stage/aliases-idf.json').then(r=>{if(!r.ok)throw Error('Alias indisponibles');return r.json();})]);
   if(data.format!=='leger-v1'||!IDF.every(d=>data.departements[d]))throw Error('Catalogue incompatible');
   window.resoudreFormationIDF=(key,index)=>{const f=index.formations.find(x=>x.k===(aliases[key]||key));return f?{...f,k:key}:null;};
   catalogue=data;
   const footer=document.querySelector('footer');
   for(const n of footer.childNodes)if(n.nodeType===3)n.textContent=n.textContent.replace(/\d{1,2} [a-zéû]+ \d{4}/u,'8 octobre 2026');
   demarrer(data);
  }catch(e){$('count').textContent='Chargement impossible. Vérifie ta connexion puis réessaie.';retry.hidden=false;}
 }
 retry.onclick=()=>catalogue?(failed='',charger()):init();
 await init();
}
