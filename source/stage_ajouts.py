"""Prépare les seuls ajouts du pilote, sans remplacer les lignes existantes.

Sans --write : bilan local seulement. Les fichiers de production et data/
historique ne sont jamais écrits. L'export LBA reste en mémoire.
"""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from stage_collecte import atomic_json, ROOT
from stage_donnees import preparer, fichier
from stage_catalogues import ecrire_catalogues
from lba import ouvrir_export, records, enrich


def lire(path):
    return json.loads(path.read_text())


def candidats(cache, deps):
    out={d:{} for d in deps}
    origins=defaultdict(set)
    for dep in deps:
        for phase, paths in [('inventaire',[cache/'departements'/(dep+'.json')]),
                             ('communes',sorted((cache/'entreprises'/dep).glob('*.json'))),
                             ('temoin',sorted((cache/'temoin'/dep).glob('*.json'))),
                             ('sondage',sorted((cache/'sondage-api/entreprises-v2'/dep).glob('*.json'))),
                             ('stock',sorted((cache/'stock-api/temoin'/dep).glob('*.json')))]:
            for p in paths:
                value=lire(p)
                if phase in ('temoin','stock') and not value['rows']:
                    # Le contrôle SIRET individuel prime sur une réponse de lot.
                    out[dep].pop(value['siret'],None)
                    continue
                for r in value['rows']:
                    out[dep][r['s']]=r
                    origins[r['s']].add(phase)
    return out,origins


def preparer_ajouts(root,cache,deps):
    catalog=lire(root/'catalogue.json')
    existing=set()
    for dep,d in catalog['departements'].items():
        for k in d['secteurs']:
            existing.update(row[7] for row in lire(root/'sirene'/dep/(k+'.json')))
    candidate,origins=candidats(cache,deps)
    groups,summary,allnew={}, {}, set()
    known=lire(ROOT/'source/verification-idf-national/entreprises-api.json')
    witness964={s for s,v in known.items() if any(e.get('etat')=='A' and e.get('diffusion')=='O' for e in v['resultat'])}
    for dep in deps:
        new={s:r for s,r in candidate[dep].items() if s not in existing}
        grouped,rejected=preparer(new.values())
        added={r[7] for rows in grouped.values() for r in rows}
        byphase=Counter()
        for s in added:
            for phase in origins[s]:byphase[phase]+=1
        direct=[lire(p) for p in (cache/'temoin'/dep).glob('*.json')]
        rejected_direct=Counter()
        for d in direct:rejected_direct.update(d['rejets'])
        geo_rejects, geo_issues = {}, Counter()
        for p in (cache/'entreprises'/dep).glob('*.json'):
            result=lire(p)
            geo_rejects.update(result['rejets'])
            # Une entreprise peut avoir plusieurs branches incertaines.
            geo_issues.update({v['motif'] for v in result['incertains']})
        rejected_geo=Counter()
        for s,reasons in geo_rejects.items():
            if s not in candidate[dep]:
                rejected_geo.update(reasons)
        summary[dep]=dict(ajoutes=len(added),deja_presents=len(candidate[dep].keys()&existing),
            lignes_ajoutees=sum(len(rows) for rows in grouped.values()),
            temoin_verifies=len(direct),temoin_ajoutes=sum(d['siret'] in added for d in direct),
            retrouves_parmi_964=len(added&witness964),
            rejets_temoin=dict(rejected_direct),rejets_classement=rejected,
            rejets_geographiques=dict(rejected_geo),incertitudes_geographiques=dict(geo_issues),
            par_methode=dict(byphase),siret_ajoutes=sorted(added))
        groups[dep]=grouped;allnew.update(added)
    return catalog,groups,summary,allnew


def ajouter_lignes(old,new):
    existing={r[7] for r in old}
    result=list(old)
    for row in new:
        if row[7] not in existing:
            result.append(row);existing.add(row[7])
    return result


def verifier_fin_pilote(cache,deps):
    # Le stock indépendant remplace le parcours géographique long, conformément
    # à la relecture. Une extraction seule ne suffit pas : tous les contrôles
    # SIRET et le sondage doivent être terminés, les limites restent au bilan.
    if (cache/'stock-verification-resultats.json').exists():
        if not lire(cache/'stock-verification-resultats.json').get('terminee'):
            raise ValueError('Pilote encore incomplet : contrôles du stock')
        tasks=lire(cache/'stock-verifications-attendues.json')['controles']
        missing=[x for x in tasks if not (cache/'stock-api/temoin'/x['dep']/(x['siret']+'.json')).is_file()]
        if missing:raise ValueError('Pilote encore incomplet : contrôles SIRET absents')
        if not (cache/'sondage-resultats.json').exists():
            raise ValueError('Pilote encore incomplet : sondage absent')
        sample=lire(cache/'sondage-resultats.json')
        if sample['echantillon']!=100 or sample['selection_a_elargir']:
            raise ValueError('Pilote encore incomplet : sondage à reprendre après élargissement')
        witnesses=lire(cache/'temoin-attendu.json')
        if any(not (cache/'temoin'/d/(s+'.json')).is_file() for d in deps for s in witnesses[d]):
            raise ValueError('Pilote encore incomplet : témoins historiques')
        return
    targets=lire(cache/'cibles.json')
    witnesses=lire(cache/'temoin-attendu.json')
    missing={}
    for dep in deps:
        absent=[s for s in targets[dep]['cibles_siren']
                if not (cache/'entreprises'/dep/(s+'.json')).is_file()]
        absent_witness=[s for s in witnesses[dep]
                        if not (cache/'temoin'/dep/(s+'.json')).is_file()]
        if absent or absent_witness:
            missing[dep]=dict(entreprises=len(absent),temoins=len(absent_witness))
    if missing:
        raise ValueError('Pilote encore incomplet : '+json.dumps(missing))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--deps',nargs='+',required=True)
    p.add_argument('--write',action='store_true')
    args=p.parse_args();root=args.root.resolve()
    if root==ROOT or not(root/'.git').exists() or set(args.deps)-{'77','93','94'}:
        p.error('Une copie séparée du dépôt de données et le seul périmètre Créteil sont requis')
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()
    if branch in ('main','master','') or not (root/'.git').is_file():
        p.error('Écriture réservée à un worktree sur une branche de travail')
    done=args.cache/'ajouts-appliques.json'
    if done.exists():
        print('Ajouts déjà appliqués ; conserver le bilan initial.');return
    if args.write:verifier_fin_pilote(args.cache,args.deps)
    catalog,groups,summary,new=preparer_ajouts(root,args.cache,args.deps)
    atomic_json(args.cache/'bilan-ajouts.json',summary)
    print(json.dumps({d:{k:v for k,v in r.items() if k!='siret_ajoutes'} for d,r in summary.items()},ensure_ascii=False),flush=True)
    if not args.write:return
    # Le flux LBA doit avoir été entièrement validé avant la moindre écriture.
    cached=args.cache/'lba-nouveaux.json'
    if cached.exists():
        lba=lire(cached)
        if lba['sirets']!=sorted(new):raise ValueError('Le cache LBA ne correspond pas aux nouveaux SIRET')
    else:
        try:
            now=datetime.now(timezone.utc)
            stream,updated=ouvrir_export(None,now)
            with stream:companies,counts=enrich(records(stream),new,now)
            if counts['opportunities']==0:raise ValueError('Export vide')
        except Exception:
            raise RuntimeError('Enrichissement LBA interrompu : aucun fichier modifié, aucun secret journalisé') from None
        lba=dict(sirets=sorted(new),entreprises=companies,compteurs=dict(counts),
                 export_le=updated,controle_le=now.isoformat())
        atomic_json(cached,lba)
    baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip():
        raise ValueError('La copie de données doit être propre avant la préparation additive')
    touched=[]
    for dep,by in groups.items():
        for k,rows in by.items():
            path=root/'sirene'/dep/(k+'.json')
            old=lire(path);combined=ajouter_lignes(old,rows)
            if combined[:len(old)]!=old:raise AssertionError('Une ligne existante a changé')
            catalog['departements'][dep]['secteurs'][k]=fichier(path,combined)
            touched.append(str(path.relative_to(root)))
    for domain in catalog['domaines']:
        for sec in domain['s']:
            sec['c']=sum(d['secteurs'][sec['k']]['n'] for d in catalog['departements'].values())
    catalog['version']=hashlib.sha256(json.dumps(catalog['departements'],sort_keys=True).encode()).hexdigest()[:16]
    atomic_json(root/'catalogue.json',catalog)
    ecrire_catalogues(root)
    bilan=lire(root/'bilan.json')
    for entry in bilan['departements']:
        dep=entry['dep']
        if dep not in args.deps:continue
        files=catalog['departements'][dep]['secteurs']
        unique={r[7] for k in files for r in lire(root/'sirene'/dep/(k+'.json'))}
        entry['apres_classement']=len(unique)
        entry['lignes']=sum(v['n'] for v in files.values())
        entry['bytes']=sum(v['bytes'] for v in files.values())+catalog['departements'][dep]['lycees']['bytes']
        entry['rattrapage']=dict(ajoutes=summary[dep]['ajoutes'],collecte_initiale_conservee=True)
    atomic_json(root/'bilan.json',bilan)
    # Mettre à jour les lignes du tableau de tailles, sans en retirer.
    sizepath=root/'tailles-fichiers.csv'
    with sizepath.open(newline='') as stream:sizerows=list(csv.DictReader(stream))
    for r in sizerows:
        if r['fichier'] in touched:
            path=root/r['fichier'];r['octets']=path.stat().st_size;r['lignes']=len(lire(path))
    with sizepath.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['fichier','octets','lignes'],lineterminator='\n')
        writer.writeheader();writer.writerows(sizerows)
    bydep={e['dep']:e for e in bilan['departements']}
    acpath=root/'bilan-academies.csv'
    with acpath.open(newline='') as stream:acrows=list(csv.DictReader(stream))
    for row in acrows:
        deps=[d.strip() for d in row['departements'].split(',')]
        if set(deps)&set(args.deps):
            row['etablissements']=sum(bydep[d]['apres_classement'] for d in deps)
            row['octets_sirene_et_lycees']=sum(bydep[d]['bytes'] for d in deps)
    with acpath.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(acrows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(acrows)
    meta=lire(root/'lba/meta.json');new_lba=set();newfiles=0
    for dep,by in groups.items():
        for k,rows in by.items():
            matching={r[7]:lba['entreprises'][r[7]] for r in rows if r[7] in lba['entreprises']}
            if not matching:continue
            path=root/'lba'/dep/(k+'.json');before=lire(path) if path.exists() else {}
            fresh={s:v for s,v in matching.items() if s not in before}
            if not fresh:continue
            atomic_json(path,dict(before,**fresh));new_lba.update(fresh)
            files=meta['files'].setdefault(dep,[])
            if k not in files:files.append(k);files.sort();newfiles+=1
    meta['matched_companies']+=len(new_lba);meta['sectors']+=newfiles
    meta['rattrapage']=dict(export_le=lba['export_le'],controle_le=lba['controle_le'],
                           nouveaux_siret=len(new_lba),departements=args.deps,
                           compteurs_nouveaux=lba['compteurs'],
                           anciens_enregistrements_inchanges=True)
    if meta['updated_at']==lba['export_le']:
        for key in ('recruiters','jobs'):
            meta['counts'][key]+=lba['compteurs'][key]
    atomic_json(root/'lba/meta.json',meta)
    report=dict(departements=summary,base_donnees=baseline,ajoutes=len(new),
                lba_nouveaux=len(new_lba),export_lba=lba['export_le'],
                perimetre='Pilote Créteil uniquement',aucun_retrait=True,
                collecte_initiale='2026-10-08',fichiers_sirene=touched)
    atomic_json(root/'rattrapage-creteil.json',report)
    atomic_json(done,report)
    print(f'{len(new)} établissements ajoutés localement ; {len(new_lba)} enrichis LBA ; rien publié.')


if __name__=='__main__':main()
