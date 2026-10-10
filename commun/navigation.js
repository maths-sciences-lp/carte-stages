/* Préférences conservées uniquement dans ce navigateur. */
import {lireAcademie} from './academie.js';
const IDF=new Set(['creteil','paris','versailles']);
export function cheminOutil(outil,academie=lireAcademie()) {
 const regional=academie&&!IDF.has(academie)&&/^[a-z-]+$/.test(academie)&&academie!=='france';
 if(outil==='accueil')return '/accueil/'+(regional?academie+'/':'');
 return (outil==='stage'?(regional?'/stage/':'/'):'/'+outil+'/')+(regional?academie+'/':'');
}
export function lireLycee(){try{return localStorage.getItem('stages.lycee');}catch(e){return null;}}
export function contexteHenaff(){
 const h=location.hash.slice(1),p=new URLSearchParams(h);
 // Les liens de classe historiques d’Après le lycée utilisent #era, #tne…
 const classe=/^\/(formation)\/(?:index.html)?$/.test(location.pathname)&&/^(era|tne|ebeniste|eeb|geometre|iccer|ma|mama|mee|mit|mnb|sdg|tma|bma-ebeniste|bma-signaletique)$/.test(h);
 return (p.get('ly')||lireLycee())==='0932119Y'||classe;
}
