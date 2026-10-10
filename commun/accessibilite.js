/* Améliorations de présentation et de navigation partagées par les quatre outils.
 * Aucun accès réseau, stockage ou modification des données métier.
 */
(()=>{
 const $=id=>document.getElementById(id);
 const annonce=document.createElement('p');annonce.className='sr-only';annonce.setAttribute('role','status');annonce.setAttribute('aria-live','polite');annonce.setAttribute('aria-atomic','true');document.body.append(annonce);
 const dire=texte=>{annonce.textContent=texte;};
 const associations={fsug:'f',qsug:'q',csug:'col',asug:'adr',lsug:'lyc','ac-suggestions':'ac-ville'};
 const visibles=e=>!!e&&!!e.getClientRects().length&&!e.closest('[hidden]');
 const retour=(box)=>$(associations[box.id]);
 // Les suggestions restent des boutons natifs : Tab / Maj+Tab, flèches et Échap.
 document.addEventListener('keydown',e=>{
  const input=e.target.closest('input'),box=input?Object.keys(associations).map($).find(b=>b&&retour(b)===input):e.target.closest('.sug,.ac-suggestions');
  if(!box||!visibles(box))return;
  const buttons=[...box.querySelectorAll('button')];
  if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();box.hidden=true;retour(box)?.focus();return;}
  if(['ArrowDown','ArrowUp'].includes(e.key)&&buttons.length){e.preventDefault();e.stopImmediatePropagation();const i=buttons.indexOf(document.activeElement);buttons[(i+(e.key==='ArrowDown'?1:-1)+buttons.length)%buttons.length].focus();}
 },true);
 // Une reconstruction de filtres ne doit pas supprimer le point de navigation.
 document.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  const box=b.closest('.sug,.ac-suggestions');
  const parent=b.parentElement.closest('[id]')||b.parentElement, id=b.id, data=[...b.attributes].filter(a=>a.name.startsWith('data-'));
  const wasFocused=document.activeElement===b;
  setTimeout(()=>{
   if(!wasFocused||visibles(b))return;
   let next=box?retour(box):(id?$(id):null);
   if(!next&&parent.isConnected&&data.length)next=[...parent.querySelectorAll('button')].find(n=>data.every(a=>n.getAttribute(a.name)===a.value));
   if(box&&!visibles(next))next=$('change')||$('ly');
   if(visibles(next))next.focus({preventScroll:true});
  });
 },true);
 const decorated=new WeakSet();
 // Émojis remplacés par les icônes au trait de commun/icones.svg (même dessin sur tous les téléphones).
 const ICONES={'👩\u200d🏫':'tableau','🏠':'maison','🏫':'batiment','📍':'epingle','📋':'liste','🗺':'carte','📞':'telephone','🚌':'bus','✅':'coche','💡':'ampoule','ℹ':'info','🌐':'globe','📊':'barres','📈':'courbe','🎯':'courbe','💶':'euro','🛏':'lit','🧭':'boussole','📮':'enveloppe','✉':'enveloppe','👉':'fleche','📄':'document','🌱':'pousse','📚':'livre','💬':'bulle','👥':'personnes','🪑':'chaise','💻':'ecran','📶':'wifi','🕘':'horloge','🤝':'coeur','🧱':'briques','🪚':'arbre','⚡':'eclair','🔧':'cle','🏭':'usine','🎨':'palette','🛍':'sac','🗂':'dossier','🍳':'toque','🥖':'pain','💇':'ciseaux','🚚':'camion','🌿':'feuille','♻':'goutte','👕':'teeshirt','🛡':'bouclier','🧪':'eprouvette','🎒':'cartable','🏢':'immeuble','🔒':'cadenas','🎓':'toque-diplome','⚙':'engrenage','⚽':'ballon','💼':'mallette','🖨':'imprimante','🚗':'voiture','🛒':'chariot','🍽':'couverts','🧵':'bobine','🩺':'croix'};
 const EMOJI=new RegExp('('+Object.keys(ICONES).sort((a,b)=>b.length-a.length).join('|')+')\uFE0F?','gu'),SVG='http://www.w3.org/2000/svg';
 function icone(id){const s=document.createElementNS(SVG,'svg');for(const[k,v]of[['class','ico'],['width','1.2em'],['height','1.2em'],['aria-hidden','true'],['focusable','false']])s.setAttribute(k,v);
  const u=document.createElementNS(SVG,'use');u.setAttribute('href','/commun/icones.svg#'+id);s.append(u);return s;}
 function iconiser(node){
  const t=node.textContent;EMOJI.lastIndex=0;if(!EMOJI.test(t))return;
  const p=node.parentElement;if(!p||p.closest('script,style,option,textarea,title,svg'))return;
  const frag=document.createDocumentFragment();let i=0;EMOJI.lastIndex=0;
  for(const m of t.matchAll(EMOJI)){if(m.index>i)frag.append(t.slice(i,m.index));frag.append(icone(ICONES[m[1]]));i=m.index+m[0].length;}
  if(i<t.length)frag.append(t.slice(i));node.replaceWith(frag);
 }
 function enhance(root){
  if(root.nodeType===3){iconiser(root);return;}
  if(root.nodeType!==1)return;
  const all=selector=>[...(root.matches(selector)?[root]:[]),...root.querySelectorAll(selector)];
  const icw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),txt=[];
  while(icw.nextNode())txt.push(icw.currentNode);
  for(const n of txt)iconiser(n);
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];
  while(walker.nextNode())nodes.push(walker.currentNode);
  for(const node of nodes){
   if(node.parentElement.closest('script,style,option,[aria-hidden="true"]'))continue;
   const m=node.textContent.match(/^(\s*)([🎯🎓🧭🤝🏫🏠📍📋🗺️💡🛏️📞🚌ℹ️🌐💶📊✅👉]+)(\s+)(?=\S)/u);
   if(m){const span=document.createElement('span');span.setAttribute('aria-hidden','true');span.textContent=m[2];node.before(document.createTextNode(m[1]),span);node.textContent=node.textContent.slice(m[1].length+m[2].length);}
  }
  for(const a of all('a[target="_blank"]')){
   if(decorated.has(a))continue;decorated.add(a);
   const label=a.getAttribute('aria-label')||a.textContent.trim();
   const card=a.closest('.li,.it,.card,.fo,.pop'),name=card?.querySelector('h3,.nm,b')?.textContent.trim();
   a.setAttribute('aria-label',label+(name?' — '+name:'')+' (nouvel onglet)');
   a.title='S’ouvre dans un nouvel onglet';
   const hint=document.createElement('span');hint.className='new-window';hint.setAttribute('aria-hidden','true');hint.textContent=' ↗';
   // Pas de seconde flèche si le texte du lien en a déjà une (ex. « Voir sur La bonne alternance ↗ »).
   if(!/↗\s*$/.test(a.textContent))a.append(hint);
  }
  for(const el of all('.dom .e,.em'))el.setAttribute('aria-hidden','true');
  for(const img of all('.leaflet-marker-icon[alt="Marker"]')){img.setAttribute('alt','Lieu sur la carte — détails dans la liste');}
 }
 enhance(document.body);
 const observer=new MutationObserver(records=>{
  for(const r of records){if(r.type==='characterData')iconiser(r.target);else for(const n of r.addedNodes)enhance(n);}
 });observer.observe(document.body,{childList:true,subtree:true,characterData:true});
 for(const [id,inputId] of Object.entries(associations)){
  // Le sélecteur d’académie est monté après ce script ; son statut est géré dans academie.js.
  const box=$(id),input=$(inputId);if(!box||!input)continue;
  input.setAttribute('aria-controls',id);
  const watch=()=>{const n=box.querySelectorAll('button').length;if(visibles(box))dire(n?`${n} proposition${n>1?'s':''}. Utilise Tab ou les flèches pour choisir.`:box.textContent.trim()||'Aucun résultat. Essaie un autre nom.');};
  new MutationObserver(watch).observe(box,{childList:true,attributes:true,attributeFilter:['hidden']});
 }
 for(const id of ['count','dmsg','amsg','lmsg','qmsg']){const e=$(id);if(e){e.setAttribute('role','status');e.setAttribute('aria-live','polite');e.setAttribute('aria-atomic','true');}}
 // Nom et alternative de la carte, sans supprimer les commandes Leaflet.
 const map=$('map');if(map){map.setAttribute('role','region');map.setAttribute('aria-label','Carte des résultats');
  const alt=document.createElement('aside');alt.setAttribute('aria-label','Alternative à la carte');alt.className='map-alternative';alt.innerHTML='Tous les lieux et leurs coordonnées sont aussi disponibles dans la <button type="button" class="btn light">Liste</button>.';
  map.before(alt);alt.querySelector('button').onclick=()=>{const b=$('vL')||$('tl');b?.click();b?.focus();};
  const sync=()=>alt.hidden=!visibles(map);new MutationObserver(sync).observe(map,{attributes:true,attributeFilter:['hidden','class']});new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:['class']});sync();
  window.addEventListener('resize',sync);
 }
 // Petite vibration quand l'élève fait un choix (téléphones Android ; ignoré ailleurs et si les animations sont réduites).
 const calme=matchMedia('(prefers-reduced-motion: reduce)');
 document.addEventListener('click',e=>{
  if(calme.matches||typeof navigator.vibrate!=='function')return;
  if(e.target.closest('button[aria-pressed],.sug button,#classes button,[role=option]'))try{navigator.vibrate(15);}catch(err){}
 });
 document.addEventListener('click',e=>{if(e.target.closest('.skip-link')){e.preventDefault();const m=$('contenu-principal');m?.focus();m?.scrollIntoView();}});
})();
