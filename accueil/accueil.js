/* Accueil : académie réglée par l'adresse (/accueil/<académie>/), choisie par l'élève
 * (mémorisée dans le téléphone) ou Île-de-France par défaut. Aucune donnée envoyée. */
import {initAcademie,lireAcademie} from '../commun/academie.js';
const IDF=new Set(['creteil','paris','versailles']); // les pages Île-de-France couvrent ces trois académies
const base=new URL('./',document.baseURI),racine=new URL('../',base);
const cartes=[...document.querySelectorAll('a.c[data-outil]')];
const lieu=document.getElementById('lieu'),mount=document.getElementById('choix-lieu');
function regler(ac){
 const idf=!ac||IDF.has(ac.slug);
 for(const a of cartes){
  const o=a.dataset.outil,dossier=o==='stage'?(idf?'':'stage/'):o+'/';
  a.href=new URL(dossier+(idf?'':ac.slug+'/'),racine).pathname;
 }
}
let lance=false;
async function demarrer(question){
 if(lance)return;lance=true;lieu.hidden=true;
 await initAcademie({mount,contenu:document.querySelector('.choix'),baseOutil:base,onSelect:async ac=>regler(ac)});
 if(question)document.getElementById('ac-title')?.focus();
}
const chemin=location.pathname.slice(base.pathname.length).split('/')[0];
if(chemin||lireAcademie())demarrer(false); // /accueil/<académie>/, /accueil/france/ ou choix déjà fait
else document.getElementById('changer-lieu').onclick=()=>demarrer(true);
