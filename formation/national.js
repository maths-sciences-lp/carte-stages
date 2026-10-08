/* Une application ; le choix d'académie vient exclusivement de commun/. */
import {initAcademie,academieDepuisAdresse} from '../commun/academie.js';
const main=document.querySelector('main'),mount=document.createElement('div');
main.querySelector('h1').after(mount);
const contenu=document.createElement('div');contenu.id='nationalContent';
const lead=main.querySelector('.lead');main.insertBefore(contenu,lead);contenu.append(lead);
for(const section of [...main.querySelectorAll(':scope > section')])contenu.append(section);
const hen=contenu.querySelector('.hen'),ou=contenu.querySelector('.ou');
const heading=ou.nextElementSibling,academyHint=heading.nextElementSibling;
const definitions=document.createElement('p');definitions.className='msg';definitions.id='definitions';$('chips').before(definitions);
const sigles={BTSA:'brevet de technicien supérieur agricole',BTS:'brevet de technicien supérieur','DN MADE':'diplôme national des métiers d’art et du design',CS:'certificat de spécialisation',BP:'brevet professionnel',BTMS:'brevet technique des métiers supérieur',BTM:'brevet technique des métiers',BNMA:'brevet national des métiers d’art'};
let active=null,seq=0,addressTimer;
const francais=s=>s.replace(/ ([?!:;])/g,'\u00a0$1');
function typo(root){
 const it=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 while(it.nextNode())it.currentNode.textContent=francais(it.currentNode.textContent);
 for(const input of root.querySelectorAll('[placeholder]'))input.placeholder=francais(input.placeholder);
}
const originalDraw=draw;
draw=()=>{originalDraw();typo(contenu);};
const originalMontrer=montrer;
montrer=user=>{
 originalMontrer(user);
 const d=D.dip[cur.d];
 if(d.a.length)$('ailleurs').innerHTML=`🧭 <b>Aussi possibles</b> : ${d.a.map(esc).join(' · ')}. Aucun lieu trouvé dans les données Onisep en ${esc(D.region)}. <a href="${esc(d.o)}" target="_blank" rel="noopener">Consulte la fiche du diplôme</a> avec ton professeur principal.`;
 const names=[...d.s.map(k=>D.suites[k].n),...d.a];
 definitions.textContent=Object.entries(sigles).filter(([k])=>names.some(n=>n.startsWith(k+' '))).map(([k,v])=>k+' : '+v).join(' · ');
 definitions.hidden=!definitions.textContent;
 $('bts').textContent=' : un BTS (brevet de technicien supérieur) est une poursuite possible après un bac professionnel';
 typo(contenu);
};
// Le message de recherche s'adapte à l'académie ; la recherche elle-même reste commune.
$('q').addEventListener('input',()=>{
 if($('qmsg').textContent)$('qmsg').textContent='Pas trouvé dans cette académie. Essaie un autre mot, comme « vente » ou « électricien ».';
});
searchAdr=async v=>{
 const r=await fetch('https://api-adresse.data.gouv.fr/search/?autocomplete=1&limit=15&q='+encodeURIComponent(v));
 if(!r.ok)throw Error('Recherche indisponible');
 return((await r.json()).features||[]).filter(f=>academieDepuisAdresse(f)?.slug===active?.slug).slice(0,5);
};
const address=$('adr').cloneNode(true);$('adr').replaceWith(address);
async function addressSearch(){
 clearTimeout(addressTimer);const request=++seq,slug=active?.slug,v=address.value.trim();$('asug').hidden=true;
 if(v.length<3)return;
 try{const rows=await searchAdr(v);if(request!==seq||slug!==active?.slug)return;sug(rows);
  $('amsg').textContent=rows.length?'':'Adresse pas trouvée. Écris le numéro, la rue et la ville.';
 }catch(e){if(request===seq)$('amsg').textContent='La recherche ne répond pas. Réessaie dans un instant.';}
}
address.addEventListener('input',()=>{++seq;clearTimeout(addressTimer);$('asug').hidden=true;addressTimer=setTimeout(addressSearch,250);});
address.addEventListener('keydown',e=>{if(e.key!=='Enter')return;e.preventDefault();const b=$('asug').querySelector('button');if(b&&!$('asug').hidden)b.click();else addressSearch();});
const footer=main.querySelector('footer');
footer.style.visibility='visible';typo(main);
await initAcademie({mount,contenu,baseOutil:new URL('./',document.baseURI),onSelect:async(ac,{signal})=>{
 async function data(name){const r=await fetch(new URL('data/'+name+'.json?v=2026-10-08b',document.baseURI),{signal});if(!r.ok)throw Error('Données indisponibles');return r.json();}
 const [d,ps]=await Promise.all([data(ac.slug),data(ac.slug+'-parcoursup')]);if(signal.aborted)return;
 active=ac;++seq;clearTimeout(addressTimer);D=d;PS=ps;cur=null;dep=null;off.clear();
 if(layer){layer.remove();layer=null;}
 for(const id of ['q','adr'])$(id).value='';
 for(const id of ['qsug','asug','lyc','res'])$(id).hidden=true;
 $('list').replaceChildren();$('chips').replaceChildren();$('qmsg').textContent='';$('amsg').textContent='';$('aide').hidden=false;
 vue(false);depart(false);
 const hasHenaff=D.classes.length>0;hen.hidden=!hasHenaff;ou.hidden=!hasHenaff;
 heading.textContent=hasHenaff?'Un autre lycée de ton académie':'Ton diplôme et ton lycée';academyHint.textContent=ac.nom;
 lead.textContent='Après ton CAP (certificat d’aptitude professionnelle), ton bac professionnel ou ton BMA (brevet des métiers d’art), découvre des poursuites d’études en '+D.region+'.';
 $('aide').textContent=hasHenaff?'Choisis d’abord ta classe ou ton diplôme.':'Choisis d’abord ton diplôme.';
 IDX=Object.entries(D.dip).map(([id,x])=>({id,lib:x.lib,n:x.ly.length,t:norm(x.lib+' '+x.al)}));drawClasses();lireHash();
 document.title='Après le lycée – '+ac.nom;document.querySelector('meta[name="description"]').content=lead.textContent;typo(main);
}});
