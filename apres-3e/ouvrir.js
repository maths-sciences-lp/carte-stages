/* Petites pages par académie : une seule application HTML, URL directe conservée. */
(async()=>{
 try {
  const base=new URL('../',location.href),r=await fetch(new URL('index.html',base));
  if(!r.ok)throw new Error('Application indisponible');
  const text=await r.text();
  const app=text.replace('<head>','<head><base href="'+base.pathname+'"><script>window.APRES3E_NATIONAL=true;<\/script><style>main>.lead,main>.step,main>footer{visibility:hidden}</style>')
   .replace('</body>','<script type="module" src="national.js"></script></body>');
  document.open();document.write(app);document.close();
 } catch(e){document.getElementById('loading').textContent='La page ne se charge pas. Vérifie ta connexion, puis recharge la page.';}
})();
