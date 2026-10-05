import json,collections,re
o=json.load(open('onisep_formations.json')); d=json.load(open('lp_idf_2025.json'))
codes={x['code_scolarite']:x for x in o if x['code_scolarite']}
def okind(x):
    t=(x['sigle_type_formation']+' '+x['libelle_formation_principal']).lower()
    if t.startswith('cap') or ' cap ' in t[:8] or x['libelle_formation_principal'].lower().startswith('cap'): return 'CAP'
    if 'bac pro' in t: return 'BAC'
    return None
G=collections.defaultdict(lambda:dict(etabs=set(),eleves=0,deps=set(),abbr=set(),dom='',url='',cfd=''))
for r in d:
    l=r['mef_bcp_6_lib_l']; mef=r['mef_bcp_11']; lab=r['mef_bcp_11_lib_l']
    if l.startswith('CAP'): k='CAP'
    elif l.startswith('BAC PRO'): k='2NDE' if '2NDE' in l else 'BAC'
    else: continue
    agri='AGRICOLE' in l
    x=None
    for p in ({'CAP':'5','BAC':'4','2NDE':'4'}[k],'5','4','3','2'):
        c=codes.get(p+mef[4:])
        if c and (okind(c)==('CAP' if k=='CAP' else 'BAC') or k=='2NDE'): x=c; break
    short=re.sub(r'^\S+\s+','',lab).strip()
    if k=='2NDE':
        name=short.replace('2NDE COMMUNE','').replace('2NDE COMM.','').replace('2NDE COM','').strip(' .')
        key=('2NDE',name)
    elif x: key=(k,x['libelle_formation_principal'])
    else: key=(k,short)
    g=G[key]
    g['etabs'].add(r['numero_d_etablissement']); g['eleves']+=r['nombre_d_eleves_total'] or 0
    g['deps'].add(r['code_departement'][-2:] if r['code_departement'] else ''); g['abbr'].add(short); g['agri']=agri
    if x: g['dom']=x['domainesous-domaine']; g['url']=x['url_et_id_onisep']; g['cfd']=x['code_scolarite']
    else: g['nomenclature']='abrégé'
out=[]
for (k,n),g in G.items():
    out.append(dict(type=k,nom=n,lycees=len(g['etabs']),eleves=g['eleves'],deps=' '.join(sorted(x for x in g['deps'] if x)),
        domaine=g['dom'],onisep=g['url'],cfd=g['cfd'],agri=g.get('agri',False),abrege='' if g['url'] else 'oui',sigles=' / '.join(sorted(g['abbr']))))
json.dump(out,open('formations_idf.json','w'),ensure_ascii=False)
c=collections.Counter(x['type'] for x in out); print(c)
print('sans nom complet:',[x['nom'] for x in out if x['abrege'] and x['type']!='2NDE'])
