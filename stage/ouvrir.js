/* Une application commune ; aucune copie du HTML historique par académie. */
(async()=>{
 try{
  const base=new URL('../../',location.href),response=await fetch(new URL('index.html',base));
  if(!response.ok)throw Error('Application indisponible');
  const html=await response.text();
  const page=html.replace('<head>','<head><base href="'+base.pathname+'"><script>window.STAGE_NATIONAL=true;<\/script><style>#contenu-principal>.lead,#contenu-principal>.step,#map{visibility:hidden}</style>')
   .replace('</body>','<script type="module" src="stage/national.js"></script></body>');
  document.open();document.write(page);document.close();
 }catch(e){document.getElementById('loading').textContent='La page ne se charge pas. Vérifie ta connexion, puis recharge la page.';}
})();
