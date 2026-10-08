/* Adaptateur : l'application et les domaines restent ceux de la page historique. */
import {initAcademie,academieDepuisAdresse} from '../commun/academie.js';
const main=document.querySelector('main'),mount=document.createElement('div');
main.querySelector('h1').after(mount);
const contenu=document.createElement('div');contenu.id='nationalContent';
const lead=main.querySelector('.lead');main.insertBefore(contenu,lead);
contenu.append(lead);
for(const section of [...main.querySelectorAll(':scope > section')])contenu.append(section);
let active=null,addressRequest=0,addressTimer;
voisinsDe=()=>active.slug;
// Académies sans lycée d'une autre académie à moins de 30 km (apres-3e/data/bilan-voisins.json) : pas de bouton.
const SANS_VOISINS=new Set(["corse", "guadeloupe", "guyane", "la-reunion", "martinique", "mayotte"]);
// AF page web peut être le site du lycée : le bouton Onisep doit ouvrir Onisep.
const originalLieuHTML=lieuHTML;
lieuHTML=({e,d})=>originalLieuHTML({e:{...e,af:e.o},d});

// Département du lycée, au lieu du filtre des trois académies propre à l'IDF.
lieux=f=>f.e.filter(e=>!offD.has(e.dep)&&(!intern||e.it))
 .map(e=>({e,d:dep?km(dep.lat,dep.lon,e.lat,e.lon):null}))
 .sort((a,b)=>a.d!==null?a.d-b.d:a.e.v.localeCompare(b.e.v));
const originalChips=chips;
chips=()=>{
 originalChips();
 const departments=[...new Set(D.formations.flatMap(f=>f.e.map(e=>e.dep)))].sort((a,b)=>a.localeCompare(b,'fr'));
 $('fdep').hidden=departments.length<2;
 $('fdep').innerHTML=departments.map(d=>`<button class="chip" data-departement="${esc(d)}" aria-pressed="${!offD.has(d)}">${esc(d)}</button>`).join('');
 $('fdep').setAttribute('aria-label','Départements des lycées');
 $('fdep').querySelectorAll('button').forEach(b=>b.onclick=()=>{
  const d=b.dataset.departement;offD.has(d)?offD.delete(d):offD.add(d);show(false);
 });
};

searchAdr=async v=>{
 const r=await fetch('https://api-adresse.data.gouv.fr/search/?autocomplete=1&limit=15&q='+encodeURIComponent(v));
 if(!r.ok)throw new Error('Recherche indisponible');
 return((await r.json()).features||[]).filter(f=>academieDepuisAdresse(f)?.slug===active?.slug).slice(0,5);
};
const address=$('adr').cloneNode(true);$('adr').replaceWith(address);
address.addEventListener('input',()=>{
 clearTimeout(addressTimer);const seq=++addressRequest,v=address.value.trim(),slug=active?.slug;
 $('asug').hidden=true;if(v.length<3)return;
 addressTimer=setTimeout(async()=>{
  try{const rows=await searchAdr(v);if(seq!==addressRequest||slug!==active?.slug)return;
   sugList($('asug'),rows,f=>f.properties.label,pickAdr);
  }catch(e){if(seq===addressRequest)$('dmsg').textContent='La recherche ne répond pas. Réessaie dans un instant.';}
 },250);
});

const francais=s=>s.replace(/ ([?!:;])/g,'\u00a0$1');
function typographie(root){
 const texts=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 while(texts.nextNode())texts.currentNode.textContent=francais(texts.currentNode.textContent);
 for(const input of root.querySelectorAll('[placeholder]'))input.placeholder=francais(input.placeholder);
}
const originalShow=show;
show=scroll=>{originalShow(scroll);typographie(contenu);};
const originalSetDep=setDep;
setDep=(...args)=>{originalSetDep(...args);typographie(contenu);};
const note=$('s3').querySelector('.note');
const conseil=`💡 <b>Bon à savoir.</b> Une <b>2de pro « famille de métiers »</b> est une seconde commune à plusieurs bacs professionnels. Tu choisis ton bac pro à la fin de l’année. Un <b>CAP (certificat d’aptitude professionnelle)</b> dure 2 ans, un <b>bac pro</b> 3 ans. L’affectation au lycée se fait par <b>Affelnet, dans ton académie</b>. Les places sont limitées. Parles-en à ton professeur principal ou au Psy-EN (psychologue de l’Éducation nationale). Pour un lycée dans une autre académie, demande au collège les démarches à suivre. Les formations en apprentissage ne sont pas encore affichées.`;
const pression=` La ligne 📈 indique les <b>premiers vœux et les places en 2025</b>. Quand les vœux dépassent beaucoup les places, ajoute d’autres vœux. Ces chiffres concernent seulement l’académie de Créteil et changent chaque année.`;
const footer=main.querySelector('footer');
// Seul le premier paragraphe de sources dépend du périmètre ; liens conservés.
const end=footer.querySelector('br');
while(footer.firstChild!==end)footer.firstChild.remove();
const sources=document.createElement('span');footer.prepend(sources);
function sourceText(ac){
 sources.innerHTML=`Données : <a href="https://opendata.onisep.fr" target="_blank" rel="noopener">Onisep</a> (formations et établissements, voie scolaire, octobre 2026) · collèges et internats : <a href="https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/" target="_blank" rel="noopener">annuaire de l’Éducation nationale</a>, internats croisés avec les fiches Onisep (« à vérifier auprès du lycée » quand les sources ne concordent pas) · devenir des élèves : <a href="https://data.education.gouv.fr/explore/dataset/fr-en-inserjeunes-lycee_pro-formation-fine/" target="_blank" rel="noopener">InserJeunes</a> (sortants 2023-2024, chiffres masqués si trop peu d’élèves).${ac?.slug==='creteil'?' Premiers vœux et places : <a href="https://orientation.ac-creteil.fr/bilans-de-laffectation-de-lorientation/" target="_blank" rel="noopener">bilan de l’affectation 2025, Draio Créteil</a> (© www.ac-creteil.fr - académie de Créteil).':''} Domaines regroupés à partir de l’indexation Onisep. Adresses : Base Adresse Nationale · carte © OpenStreetMap · localisation de l’académie : contours Etalab/IGN, Licence Ouverte.`;
}
sourceText(null);typographie(main);footer.style.visibility='visible';
await initAcademie({mount,contenu,baseOutil:new URL('./',document.baseURI),onSelect:async(ac,{signal})=>{
 const r=await fetch(new URL('data/'+ac.slug+'.json?v=2026-10-08',document.baseURI),{signal});
 if(!r.ok)throw new Error('Données indisponibles');
 const data=await r.json();if(signal.aborted)return;
 for(const f of data.formations)for(const e of f.e)e.n=e.n.replace(/Eug[eè]ne Henaff/g,'Eugène Hénaff'); // nom officiel accentué
 ++addressRequest;clearTimeout(addressTimer);active=ac;fermerVoisins();$('cvois').parentElement.hidden=SANS_VOISINS.has(ac.slug);D=data;dep=null;q='';offT.clear();offD.clear();intern=false;open.clear();
 for(const id of ['adr','col','q'])$(id).value='';
 $('csug').hidden=true;$('asug').hidden=true;
 $('dmsg').textContent='Choisis ton collège ou ton adresse pour voir les lycées les plus proches.';
 if(layer){layer.remove();layer=null;}
 mode('col');vue(false);
 lead.textContent='Les CAP (certificats d’aptitude professionnelle), secondes professionnelles et bacs professionnels — '+ac.nom+'. Choisis ce qui te plaît, puis ton point de départ.';
 note.innerHTML=conseil+(ac.slug==='creteil'?pression:'');sourceText(ac);
 const k=location.hash.slice(1);dom=(k==='tout'||D.domaines.some(d=>d.k===k))?k:null;
 $('res').hidden=true;$('aide').hidden=false;drawDoms();if(dom)show(false);
 document.title='Après le collège – '+ac.nom;typographie(main);
 document.querySelector('meta[name="description"]').content=lead.textContent;
}});
