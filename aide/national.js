/* Adaptateur de l'application aide/index.html au sélecteur partagé. */
import {initAcademie,academieDepuisAdresse} from '../commun/academie.js';
const main=document.querySelector('main'),mount=document.createElement('div');
main.querySelector('h1').after(mount);
const contenu=document.createElement('div');contenu.id='nationalContent';
const lead=main.querySelector('.lead');main.insertBefore(contenu,lead);
// Les trois étapes sont inchangées ; les numéros d'écoute restent toujours accessibles.
contenu.append(lead);
for(const section of [...main.querySelectorAll(':scope > section')].slice(0,3))contenu.append(section);
const reveal=document.createElement('style');reveal.textContent='main>.step{visibility:visible}';document.head.append(reveal);
let active=null;
chips=()=>{$('fdep').hidden=true;};
searchAdr=async v=>{
 const r=await fetch('https://api-adresse.data.gouv.fr/search/?autocomplete=1&limit=15&q='+encodeURIComponent(v));
 if(!r.ok)throw new Error('Recherche indisponible');
 return((await r.json()).features||[]).filter(f=>academieDepuisAdresse(f)?.slug===active?.slug).slice(0,5);
};
// Une réponse ancienne de la recherche d'adresse ne doit pas changer l'académie suivante.
const address=$('adr').cloneNode(true);$('adr').replaceWith(address);
let addressTimer,addressRequest=0;
address.addEventListener('input',()=>{
 clearTimeout(addressTimer);const seq=++addressRequest,v=address.value.trim(),slug=active?.slug;
 $('asug').hidden=true;if(v.length<3)return;
 addressTimer=setTimeout(async()=>{
  try{const rows=await searchAdr(v);if(seq!==addressRequest||slug!==active?.slug)return;
   sugList($('asug'),rows,f=>f.properties.label,pickAdr);
  }catch(e){if(seq===addressRequest)$('dmsg').textContent='La recherche ne répond pas. Réessaie dans un instant.';}
 },250);
});
// Typographie du parcours national, sans modifier le rendu historique.
const francais=s=>s.replace(/ ([?!:;])/g,'\u00a0$1');
for(const item of SIT)for(const key of ['n','s'])item[key]=francais(item[key]);
const texts=document.createTreeWalker(main,NodeFilter.SHOW_TEXT);
while(texts.nextNode())texts.currentNode.textContent=francais(texts.currentNode.textContent);
const note=$('s3').querySelector('.note');
note.innerHTML=note.innerHTML.replace('au CPE,','au CPE (conseiller principal d’éducation),').replace('au Psy-EN.','au Psy-EN (psychologue de l’Éducation nationale).');
const ars=main.querySelector('footer a[href*="iledefrance.ars"]');
if(ars){ars.previousSibling.textContent=ars.previousSibling.textContent.replace('liste de l’','');ars.nextSibling.textContent='annuaire de l’';ars.remove();}
const nationalFooter=document.createElement('p');nationalFooter.textContent='Localisation de l’académie : contours Etalab/IGN, Licence Ouverte.';
main.querySelector('footer').prepend(nationalFooter);
await initAcademie({mount,contenu,baseOutil:new URL('./',document.baseURI),onSelect:async(ac,{signal})=>{
 const response=await fetch(new URL('data/'+ac.slug+'.json?v=2026-10-08',document.baseURI),{signal});
 if(!response.ok)throw new Error('Données indisponibles');
 const data=await response.json();if(signal.aborted)return;
 ++addressRequest;active=ac;D=data;dep=null;offD.clear();nmax=8;
 $('adr').value='';$('col').value='';$('csug').hidden=true;$('asug').hidden=true;
 $('dmsg').textContent='Indique ta ville ou ton adresse pour voir les lieux les plus proches.';
 if(layer){layer.remove();layer=null;}
 lead.textContent='Des lieux gratuits pour les jeunes — '+ac.nom+', du plus proche au plus éloigné.';
 const k=location.hash.slice(1);sit=(k==='tout'||SIT.some(s=>s.k===k))?k:null;
 $('res').hidden=true;$('aide').hidden=false;drawSit();show(false);
 document.title='Qui peut m’aider ? – '+ac.nom;
}});
