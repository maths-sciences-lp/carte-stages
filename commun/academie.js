/* Sélecteur commun aux versions nationales. Aucune bibliothèque, aucune position envoyée.
 * initAcademie({mount, contenu, onSelect, baseOutil}) ; onSelect(academie, {signal}).
 * Les anciennes pages Île-de-France ne chargent pas ce module.
 */
const asset = name => new URL(name, import.meta.url);
const KEY = 'stages.academie';
let catalogue, chargement, contours;
const formes=new Map();
async function json(url) {
 const r=await fetch(url);if(!r.ok)throw new Error('Chargement impossible');return r.json();
}
export async function chargerAcademies() {
 if(!chargement)chargement=json(asset('academies.json')).then(d=>catalogue=d).catch(e=>{chargement=null;throw e;});
 return chargement;
}
export function academieDepuisDepartement(code) {
 // Aucun arbitrage silencieux en cas de département inconnu ou ambigu.
 const matches=(catalogue||[]).filter(a=>a.deps.includes(String(code)));
 return matches.length===1?matches[0]:null;
}
export function academieDepuisAdresse(resultat) {
 const code=String(resultat?.properties?.citycode||'');
 return academieDepuisDepartement(/^(97|98)/.test(code)?code.slice(0,3):code.slice(0,2));
}
export function lireAcademie() {try{return localStorage.getItem(KEY);}catch(e){return null;}}
export function retenirAcademie(slug) {try{localStorage.setItem(KEY,slug);}catch(e){}window.dispatchEvent(new Event('stages:academie'));}
export function academieDepuisURL(baseOutil) {
 const base=new URL(baseOutil,location.href).pathname.replace(/\/?$/,'/');
 if(!location.pathname.startsWith(base))return null;
 const slug=location.pathname.slice(base.length).split('/')[0];
 return (catalogue||[]).find(a=>a.slug===slug)||null;
}
function inRing(x,y,ring) {
 let inside=false;
 for(let i=0,j=ring.length-1;i<ring.length;j=i++) {
  const [xi,yi]=ring[i],[xj,yj]=ring[j];
  if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)inside=!inside;
 }
 return inside;
}
export function departementDepuisPosition(lat,lon,data) {
 const matches=data.features.filter(f=>{
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
  return polygons.some(p=>inRing(lon,lat,p[0])&&!p.slice(1).some(r=>inRing(lon,lat,r)));
 });
 return matches.length===1?matches[0].properties.code:null;
}
export async function initAcademie({mount,contenu,onSelect,baseOutil}) {
 const base=new URL(baseOutil,location.href);
 const style=document.createElement('style');
 style.textContent=`.ac-picker{background:#fff;border:1px solid #e4e9ee;border-radius:18px;padding:16px;margin:14px 0;color:#15314f}.ac-picker h2{font-size:24px}.ac-picker button,.ac-picker input{font:inherit;min-height:48px;border-radius:12px;width:100%;padding:11px 12px;box-sizing:border-box}.ac-picker button{cursor:pointer}.ac-geo{border:0;background:#15314f;color:white;font-weight:600;margin:8px 0 14px}.ac-picker input{border:2px solid #e4e9ee;margin-top:6px}.ac-picker summary{padding:14px 0;cursor:pointer}.ac-options,.ac-suggestions{display:grid;gap:6px}.ac-options button,.ac-suggestions button{border:1px solid #e4e9ee;background:#f5f7f9;color:#15314f;text-align:left}.ac-msg{font-size:15px;color:#667085}.ac-bar{font-size:15px;margin:12px 0}.ac-bar button{font:inherit;background:none;border:0;padding:10px;color:#2a4f7c;text-decoration:underline;cursor:pointer}.ac-picker [hidden],.ac-bar[hidden]{display:none!important}`;
 document.head.append(style);
 mount.innerHTML=`<div class="ac-bar" hidden><span></span> · <button type="button">changer</button></div>
 <section class="ac-picker" aria-labelledby="ac-title" hidden>
  <h2 id="ac-title" tabindex="-1">Tu habites où ?</h2>
  <button type="button" class="ac-geo">📍 Me localiser</button>
  <label for="ac-ville">Tape ta ville</label>
  <input id="ac-ville" type="text" placeholder="Par exemple : Lyon" autocomplete="address-level2" aria-controls="ac-suggestions">
  <div id="ac-suggestions" class="ac-suggestions" hidden></div>
  <p class="ac-msg ac-status" role="status" aria-live="polite"></p>
  <details><summary>Je connais mon académie</summary>
   <p class="ac-msg">Une académie, c’est la zone de l’Éducation nationale dont dépend ton lycée.</p>
   <div class="ac-options"></div>
  </details>
 </section>`;
 const el=s=>mount.querySelector(s),picker=el('.ac-picker'),bar=el('.ac-bar'),status=el('.ac-status'),input=el('input'),geo=el('.ac-geo'),suggestions=el('.ac-suggestions');
 let sequence=0,search=0,timer,controller;
 function message(s){status.textContent=s;}
 function urlPour(slug){return new URL(slug+'/',base).pathname+location.hash;}
 function question(focus=true) {
  ++sequence;++search;controller?.abort();geo.disabled=false;
  contenu.hidden=true;bar.hidden=true;picker.hidden=false;
  input.value='';suggestions.hidden=true;message('');
  // Le choix précédent reste mémorisé, mais cette URL demande explicitement de choisir.
  history.replaceState(null,'',urlPour('france'));
  if(focus){el('h2').focus();picker.scrollIntoView({block:'start'});}
 }
 async function choisir(ac,choixUtilisateur=true) {
  const seq=++sequence;++search;controller?.abort();controller=new AbortController();geo.disabled=false;
  suggestions.hidden=true;message('Chargement des lieux…');
  try {
   await onSelect(ac,{signal:controller.signal});
   if(seq!==sequence)return;
   retenirAcademie(ac.slug);history.replaceState(null,'',urlPour(ac.slug));
   el('.ac-bar span').textContent='📍 '+ac.nom;bar.hidden=false;picker.hidden=true;contenu.hidden=false;message('');
   if(choixUtilisateur){const titre=contenu.querySelector('h2')||contenu;titre.tabIndex=-1;titre.focus();}
  } catch(e) {
   if(seq!==sequence)return;
   picker.hidden=false;contenu.hidden=true;bar.hidden=true;
   message('Les données ne se chargent pas. Choisis ton académie pour réessayer.');
  }
 }
 function fallback(seq,text) {if(seq!==sequence)return;geo.disabled=false;message(text);input.focus();}
 el('.ac-bar button').onclick=()=>question();
 input.addEventListener('input',()=>{
  clearTimeout(timer);const request=++search,q=input.value.trim();suggestions.hidden=true;
  if(q.length<3)return;
  timer=setTimeout(async()=>{
   try {
    await chargerAcademies();
    const r=await json('https://api-adresse.data.gouv.fr/search/?type=municipality&autocomplete=1&limit=8&q='+encodeURIComponent(q));
    if(request!==search||picker.hidden)return;
    const rows=(r.features||[]).filter(f=>academieDepuisAdresse(f));suggestions.replaceChildren();
    rows.forEach(f=>{const b=document.createElement('button');b.type='button';b.textContent=f.properties.label+(f.properties.postcode&&!f.properties.label.includes(f.properties.postcode)?' ('+f.properties.postcode+')':'');b.onclick=()=>choisir(academieDepuisAdresse(f));suggestions.append(b);});
    suggestions.hidden=!rows.length;message(rows.length?'Choisis ta ville.':'Aucune ville trouvée. Essaie son code postal ou choisis ton académie ci-dessous.');
   } catch(e){if(request===search)message('La recherche ne répond pas. Réessaie ou choisis ton académie ci-dessous.');}
  },300);
 });
 geo.onclick=()=>{
  const seq=++sequence;
  if(!navigator.geolocation){fallback(seq,'La localisation n’est pas disponible. Tape ta ville.');return;}
  geo.disabled=true;message('Je cherche ton académie…');
  navigator.geolocation.getCurrentPosition(async p=>{
   try {
    await chargerAcademies();
    if(!contours)contours=json(asset('departements.json')).catch(e=>{contours=null;throw e;});
    const {latitude:lat,longitude:lon}=p.coords;
    const possibles=(await contours).filter(d=>lon>=d.bbox[0]&&lat>=d.bbox[1]&&lon<=d.bbox[2]&&lat<=d.bbox[3]);
    const features=await Promise.all(possibles.map(d=>{
     if(!formes.has(d.code))formes.set(d.code,json(asset('contours/'+d.code+'.json')).catch(e=>{formes.delete(d.code);throw e;}));
     return formes.get(d.code);
    }));
    const code=departementDepuisPosition(lat,lon,{features});
    if(seq!==sequence||picker.hidden)return;
    const ac=academieDepuisDepartement(code);
    if(!ac){fallback(seq,'Je ne trouve pas ton académie ici. Tape ta ville.');return;}
    await choisir(ac);
   } catch(e){fallback(seq,'La localisation ne répond pas. Tape ta ville.');}
  },()=>fallback(seq,'La localisation n’a pas fonctionné. Tape ta ville.'),{timeout:10000,maximumAge:60000});
 };
 contenu.hidden=true;picker.hidden=false;message('Chargement…');
 try {
  await chargerAcademies();
  [...catalogue].sort((a,b)=>a.nom.localeCompare(b.nom,'fr')).forEach(ac=>{
   const b=document.createElement('button');b.type='button';b.textContent=ac.nom;b.onclick=()=>choisir(ac);el('.ac-options').append(b);
  });
  const direct=academieDepuisURL(base),saved=catalogue.find(a=>a.slug===lireAcademie());
  if(direct||saved)await choisir(direct||saved,false);else question(false);
 } catch(e){message('La liste ne se charge pas. Vérifie ta connexion, puis recharge la page.');}
 return {changer:question,choisir};
}
