/* Source unique Sirene/LBA. Le manifeste détaillé attend le choix de formation. */
const DATA = new URL('https://maths-sciences-lp.github.io/carte-stages-donnees/');
const cache = new Map();
export async function json(path, {signal, version, optional=false}={}) {
 const url=new URL(path,DATA);if(version)url.searchParams.set('v',version);
 const r=await fetch(url,{signal,cache:version?'default':'no-cache'});
 if(!r.ok){if(optional)return null;throw Error('Données indisponibles');}
 return r.json();
}
export function memo(key, callback) {
 if(!cache.has(key))cache.set(key,callback().catch(e=>{cache.delete(key);throw e;}));
 return cache.get(key);
}
export async function secteur(catalogue, dep, key, meta) {
 const info=catalogue.departements[dep];
 const manifest=await memo('manifest/'+dep+'/'+info.manifeste,
  ()=>json('manifestes/'+dep+'.json',{version:info.manifeste}));
 const file=manifest[key];if(!file?.n)return [];
 const rows=await memo('sirene/'+dep+'/'+key+'/'+file.sha256,
  ()=>json('sirene/'+dep+'/'+key+'.json',{version:file.sha256}));
 if(meta?.files?.[dep]?.includes(key)) {
  const lba=await memo('lba/'+dep+'/'+key+'/'+meta.updated_at,
   ()=>json('lba/'+dep+'/'+key+'.json',{version:meta.updated_at,optional:true})).catch(()=>null);
  if(lba)LBAC[key]=Object.assign(LBAC[key]||{},lba);
 }
 return rows;
}
export async function alternance() {
 // Métadonnées également différées jusqu'au premier choix de formation.
 const meta=await memo('lba-meta',()=>json('lba/meta.json',{optional:true})).catch(()=>null);
 if(!meta)return null;
 LBA=meta;
 const footer=$('lba-source');
 if(lbaAge()<=(meta.recruiter_max_age_days||31)*DAY){
  footer.hidden=false;footer.textContent='Indications La bonne alternance du '+new Date(meta.updated_at).toLocaleDateString('fr-FR')+'. Un recruteur en alternance ne garantit pas un accueil en stage.';
 }
 return meta;
}
