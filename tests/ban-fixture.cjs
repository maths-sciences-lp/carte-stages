/* Réponses enregistrées du service national des adresses (BAN, api-adresse.data.gouv.fr)
   pour les tests navigateur. Le service est parfois lent : les tests ne doivent pas en dépendre.

   Usage dans un test Playwright :
     const ban=require('../../tests/ban-fixture.cjs');
     const c=await browser.newContext(...);await ban.brancher(c);
     ...
     ban.verifier(); // à la fin : échoue si une requête BAN n'avait pas de réponse enregistrée

   Mode normal (défaut, et en CI) : chaque requête BAN reçoit la réponse enregistrée dans
   tests/fixtures/ban/<sha1>.json, sans aucun appel réseau. Une requête sans réponse enregistrée
   reçoit une erreur 503, son adresse est affichée aussitôt puis à la sortie, et le test échoue.

   Mode enregistrement : BAN_ENREGISTRER=1 laisse passer vers le vrai service et enregistre
   chaque réponse (clé = sha1 du chemin + requête, paramètres triés). Pour tout réenregistrer :
     rm tests/fixtures/ban/*.json, puis relancer chaque test concerné avec BAN_ENREGISTRER=1. */
const crypto=require('node:crypto'),fs=require('node:fs'),path=require('node:path');

const DOSSIER=path.join(__dirname,'fixtures','ban');
const ENREGISTRER=process.env.BAN_ENREGISTRER==='1';
const ENTETES={'content-type':'application/json; charset=utf-8','access-control-allow-origin':'*'};
const manquantes=new Set(),echecs=new Set();

function cle(url) {
 const u=new URL(url);u.searchParams.sort();
 return crypto.createHash('sha1').update(u.pathname+'?'+u.searchParams.toString()).digest('hex');
}
const fichierPour=url=>path.join(DOSSIER,cle(url)+'.json');

async function brancher(context) {
 await context.route('https://api-adresse.data.gouv.fr/**',async route=>{
  const url=route.request().url(),fichier=fichierPour(url);
  if(ENREGISTRER) {
   try {
    const r=await route.fetch({timeout:60000});const texte=await r.text();
    if(r.ok()) {
     fs.mkdirSync(DOSSIER,{recursive:true});
     fs.writeFileSync(fichier,JSON.stringify({url,corps:JSON.parse(texte)})+'\n');
    } else {echecs.add(url+' (statut '+r.status()+')');console.error('BAN (enregistrement) : statut '+r.status()+' pour '+url+', rien enregistré');}
    await route.fulfill({response:r,body:texte});
   } catch(e) {
    echecs.add(url+' ('+e.message.split('\n')[0]+')');console.error('BAN (enregistrement) : pas de réponse pour '+url);
    await route.abort().catch(()=>{});
   }
   return;
  }
  if(!fs.existsSync(fichier)) {
   if(!manquantes.has(url))console.error('BAN : aucune réponse enregistrée pour '+url+'\n  fichier attendu : '+path.relative(process.cwd(),fichier)+'\n  relancer ce test avec BAN_ENREGISTRER=1 pour l’enregistrer.');
   manquantes.add(url);
   await route.fulfill({status:503,headers:ENTETES,body:JSON.stringify({erreur:'Réponse BAN non enregistrée pour ce test'})});
   return;
  }
  const {corps}=JSON.parse(fs.readFileSync(fichier,'utf8'));
  await route.fulfill({status:200,headers:ENTETES,body:JSON.stringify(corps)});
 });
}

function verifier() {
 if(manquantes.size)throw new Error('Requêtes BAN sans réponse enregistrée (relancer avec BAN_ENREGISTRER=1) :\n'+[...manquantes].join('\n'));
 if(echecs.size)throw new Error('Enregistrement BAN incomplet, le service n’a pas répondu pour :\n'+[...echecs].join('\n'));
}

// Même si le test s'arrête avant verifier() (délai dépassé), la cause reste visible à la fin.
process.on('exit',()=>{
 if(manquantes.size){console.error('\nRequêtes BAN sans réponse enregistrée (relancer avec BAN_ENREGISTRER=1) :\n'+[...manquantes].join('\n'));process.exitCode=1;}
 if(echecs.size){console.error('\nEnregistrement BAN incomplet :\n'+[...echecs].join('\n'));process.exitCode=1;}
});

module.exports={brancher,verifier,cle,DOSSIER,ENREGISTRER};
