/* Pages /accueil/<académie>/ : la même page d'accueil, réglée par l'adresse. */
(async()=>{
 try{
  const base=new URL('../',location.href),r=await fetch(new URL('index.html',base));
  if(!r.ok)throw new Error('Accueil indisponible');
  const page=(await r.text()).replace('<head>','<head><base href="'+base.pathname+'">');
  document.open();document.write(page);document.close();
 }catch(e){document.getElementById('loading').textContent='La page ne se charge pas. Vérifie ta connexion, puis recharge la page.';}
})();
