/* Accueil : académie réglée par l'adresse (/accueil/<académie>/), choisie par l'élève
 * (mémorisée dans le téléphone) ou Île-de-France par défaut. Aucune donnée envoyée. */
import {initAcademie,lireAcademie} from '../commun/academie.js';
import {cheminOutil} from '../commun/navigation.js';
const base=new URL('./',document.baseURI),racine=new URL('../',base);
const cartes=[...document.querySelectorAll('a.c[data-outil]')];
const lieu=document.getElementById('lieu'),mount=document.getElementById('choix-lieu');
function regler(ac){
 for(const a of cartes)a.href=cheminOutil(a.dataset.outil,ac?.slug);
}
let lance=false;
async function demarrer(question){
 if(lance)return;lance=true;lieu.hidden=true;
 await initAcademie({mount,contenu:document.querySelector('.choix'),baseOutil:base,onSelect:async ac=>regler(ac),
  annuler:()=>{mount.replaceChildren();lieu.hidden=false;lance=false;history.replaceState(null,'',base.pathname);document.getElementById('changer-lieu').focus();}});
 if(question)document.getElementById('ac-title')?.focus();
}
const chemin=location.pathname.slice(base.pathname.length).split('/')[0];
if(chemin||lireAcademie())demarrer(false); // /accueil/<académie>/, /accueil/france/ ou choix déjà fait
document.getElementById('changer-lieu').onclick=()=>demarrer(true);
