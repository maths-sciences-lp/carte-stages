import {cheminOutil,lireLycee,contexteHenaff} from './navigation.js';
const liens=[['accueil','Tous les outils'],['stage','Trouve ton stage'],['apres-3e','Après le collège'],['formation','Après le lycée'],['aide','Qui peut m’aider ?'],['lycee','Mon lycée'],['faq','Questions fréquentes'],['faq/#vie-privee','Vie privée'],['accessibilite','Accessibilité']];
for(const mount of document.querySelectorAll('[data-pied-commun]')){
 const nav=document.createElement('nav');nav.setAttribute('aria-label','Tous les outils et informations');
 liens.forEach(([outil,label],i)=>{if(i){const sep=document.createElement('span');sep.className='sep';sep.setAttribute('aria-hidden','true');sep.textContent=' · ';nav.append(sep);}const a=document.createElement('a');a.textContent=label;a.href='/'+outil+(outil.includes('#')?'':'/');if(i<5)a.dataset.outil=outil;nav.append(a);});
 mount.append(nav);
}
let nomPromise;
async function actualiser(){
 for(const a of document.querySelectorAll('a[href]')){
  const url=new URL(a.getAttribute('href'),document.baseURI);
  if(url.origin!==location.origin||url.hash)continue; // Conserver les liens de classe et de formation précis.
  const match=url.pathname.match(/^\/(accueil|stage|apres-3e|formation|aide)\/(?:[a-z-]+\/)?$/);
  const outil=a.dataset.outil||(url.pathname==='/'?'stage':match?.[1]);
  // Les liens « ailleurs en France » servent à changer explicitement de zone.
  if(outil&&!url.pathname.endsWith('/france/'))a.href=cheminOutil(outil)+url.search+url.hash;
 }
 const henaff=contexteHenaff()&&(!window.FORMATION_NATIONAL||!!document.querySelector('#classes button'));
 for(const el of document.querySelectorAll('[data-henaff]'))el.hidden=!henaff;
 const accueil=document.querySelector('[data-mon-lycee]'),u=lireLycee();
 if(accueil){
  const texte=accueil.querySelector('[data-lycee-texte]');texte?.dataset.defaut||(texte&&(texte.dataset.defaut=texte.textContent));
  accueil.href='/lycee/';if(texte)texte.textContent=texte.dataset.defaut;else accueil.textContent='Ton lycée a sa page';
  if(u)try{
   nomPromise ||= fetch('/lycee/data/index.json').then(r=>{if(!r.ok)throw Error();return r.json();}).catch(e=>{nomPromise=null;throw e;});
   const row=(await nomPromise).find(r=>r[0]===u);
   if(row&&lireLycee()===u){accueil.href='/lycee/#'+u;const nom=row[1].replace(/Eug[eè]ne Henaff/g,'Eugène Hénaff');if(texte)texte.textContent=nom+'\u00a0: ses formations, la carte des stages et la suite après le diplôme.';else accueil.textContent='Ouvrir la page du lycée '+nom.replace(/^Lycée\s+/i,'');}
  }catch(e){/* Le lien de recherche reste utilisable hors connexion. */}
 }
}
actualiser();
for(const event of ['stages:academie','stages:lycee','hashchange','storage','pageshow'])window.addEventListener(event,actualiser);
const count=document.getElementById('count');
if(count){
 const box=document.createElement('div');box.className='partage-recherche';
 const button=document.createElement('button');button.type='button';button.textContent='Envoyer cette recherche';
 const message=document.createElement('p');message.setAttribute('role','status');message.setAttribute('aria-live','polite');
 box.append(button,message);count.after(box);
 button.onclick=async()=>{
  message.textContent='';if(typeof window.stat==='function')window.stat('partager','Envoyer cette recherche');
  const url=location.href;
  try{
   if(navigator.share){await navigator.share({title:document.title,url});return;}
   await navigator.clipboard.writeText(url);message.textContent='Lien copié';
  }catch(e){
   if(e.name==='AbortError')return;
   message.textContent='Copie l’adresse en haut de la page pour envoyer cette recherche.';
  }
 };
}
