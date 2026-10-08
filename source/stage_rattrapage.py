"""Pilote reprenable et additif ; périmètre explicite, jamais de défaut national.

Les réponses brutes, dirigeants et contacts ne sont pas enregistrés. Le cache
séparé contient uniquement les entreprises diffusibles non individuelles et
les preuves minimales de rejet. Chaque phase doit être demandée explicitement.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import time

from stage_collecte import (Collector, CODES, EFFECTIFS, ROOT, atomic_json,
                            configurer_cache, conserver, couverture)
from stage_donnees import preparer


def maintenant():
    return datetime.now(timezone.utc).isoformat()


def admissible(h, e, dep, rejected):
    # Les recherches directes SIRET ignorent les filtres de requête.
    if h.get('etat_administratif') != 'A':
        rejected['unite_non_active'] += 1
        return
    if h.get('activite_principale') not in CODES:
        rejected['naf_unite_hors_liste'] += 1
        return
    if h.get('tranche_effectif_salarie') not in EFFECTIFS:
        rejected['effectif_hors_liste'] += 1
        return
    return conserver(h, e, dep, rejected)


def temoin(root, national, deps):
    index = json.loads((root/'data/index.json').read_text())
    old = {row[7]: row for d in index['domaines'] for s in d['s']
           for row in json.loads((root/'data'/(s['k']+'.json')).read_text())}
    present = {row[7] for d in ['75','77','78','91','92','93','94','95']
               for p in (national/'sirene'/d).glob('*.json')
               for row in json.loads(p.read_text())}
    out = {dep: [] for dep in deps}
    for s in sorted(old.keys()-present):
        codes = re.findall(r'\b(\d{5})\b', old[s][2])
        if not codes:
            raise ValueError('Département du témoin indéterminé : '+s)
        dep = codes[-1][:2]
        if dep in out:
            out[dep].append(s)
    return out


class Rattrapage(Collector):
    def verifier_siret(self, item):
        dep, siret = item
        path = self.cache/'temoin'/dep/(siret+'.json')
        if path.exists():
            return json.loads(path.read_text())
        params = dict(q=siret, per_page=1, minimal='true', include='matching_etablissements,siege')
        result = self.get(params)
        rejected, rows, companies, communes, found = Counter(), [], [], [], False
        for h in result['results']:
            entries = {e.get('siret'): e for e in [h.get('siege') or {}]+(h.get('matching_etablissements') or [])}
            if siret not in entries:
                continue
            found = True
            e = entries[siret]
            row = admissible(h, e, dep, rejected)
            if row:
                rows.append(row)
                companies.append(couverture(dict(h, matching_etablissements=[e]), dep))
                communes.append(e.get('commune'))
        if not found:
            rejected['siret_introuvable'] += 1
        value = dict(siret=siret, dep=dep, date=maintenant(), rows=rows,
                     entreprises=companies, communes=communes, rejets=dict(rejected))
        atomic_json(path, value)
        return value

    def groupe_communes(self, dep, company, communes):
        """Recherche par nom + géographie, puis identité SIREN exacte obligatoire.

        q=SIREN ne doit jamais être utilisé : il désactive la géographie.
        Les branches sans résultat sont arrêtées ; les branches positives sont
        découpées jusqu'à la commune. Pas de balayage de toutes les entreprises.
        """
        siren = company['siren']
        key = hashlib.sha256(json.dumps([company,communes],sort_keys=True).encode()).hexdigest()
        path = self.cache/'communes'/dep/siren/(key+'.json')
        if path.exists():
            return json.loads(path.read_text())
        name = str(company.get('nom') or '').strip()
        if not name or re.fullmatch(r'\d{9}|\d{14}',name):
            value = dict(communes=communes,rows=[],rejets={},trouve=False,incertain='nom_non_interrogeable')
            atomic_json(path,value)
            return value
        params = dict(q=name,code_commune=','.join(communes),
                      activite_principale=company['naf'],tranche_effectif_salarie=company['effectif'],
                      etat_administratif='A',per_page=25,limite_matching_etablissements=100,
                      minimal='true',include='matching_etablissements')
        page, pages, found, rows, rejects, raw = 1, 1, False, {}, {}, set()
        uncertain = None
        while page <= pages:
            response = self.get(dict(params,page=page))
            if response['total_results'] >= 10000:
                uncertain = 'plafond_recherche_nom'
                found = True  # imposer un découpage géographique
                break
            pages = int(response['total_pages'])
            for h in response['results']:
                if h['siren'] != siren:
                    continue
                found = True
                for e in h.get('matching_etablissements') or []:
                    # Le contrôle client ne fait confiance ni au nom ni au filtre API.
                    if e.get('commune') not in communes:
                        continue
                    raw.add(e['siret'])
                    rejected = Counter()
                    row = admissible(h,e,dep,rejected)
                    if row:
                        rows[row['s']] = row
                    elif rejected:
                        rejects[e['siret']] = dict(rejected)
                if len(h.get('matching_etablissements') or []) >= 100:
                    uncertain = 'liste_saturee'
            if found:
                break
            page += 1
        value = dict(communes=communes,rows=list(rows.values()),rejets=rejects,
                     trouve=found,siret_recus=sorted(raw),incertain=uncertain,date=maintenant())
        atomic_json(path,value)
        return value

    def entreprise(self, item):
        dep, company, communes = item
        path = self.cache/'entreprises'/dep/(company['siren']+'.json')
        if path.exists():
            return json.loads(path.read_text())
        rows, rejects, issues, calls = {}, {}, [], 0
        def visiter(codes):
            nonlocal calls
            value = self.groupe_communes(dep,company,codes)
            calls += 1
            rows.update({r['s']:r for r in value['rows']})
            rejects.update(value['rejets'])
            if value.get('incertain') == 'nom_non_interrogeable':
                issues.append(dict(communes=codes,motif=value['incertain']))
                return
            if not value['trouve']:
                if codes == communes:
                    issues.append(dict(communes=codes,motif='entreprise_non_retrouvee_par_nom'))
                return
            if len(codes) == 1:
                if value.get('incertain'):
                    issues.append(dict(communes=codes,motif=value['incertain']))
                return
            mid = len(codes)//2
            visiter(codes[:mid]);visiter(codes[mid:])
        visiter(communes)
        value = dict(siren=company['siren'],dep=dep,rows=list(rows.values()),
                     rejets=rejects,incertains=issues,groupes_communes=calls,date=maintenant())
        atomic_json(path,value)
        return value


def run_inventory(collector, args):
    witness = temoin(ROOT, args.donnees, args.deps)
    atomic_json(args.cache/'temoin-attendu.json', witness)
    print('TÉMOIN : '+str({d:len(s) for d,s in witness.items()}), flush=True)
    tasks = [(d,s) for d, ss in witness.items() for s in ss]
    with ThreadPoolExecutor(max_workers=5) as pool:
        for n, _ in enumerate(pool.map(collector.verifier_siret, tasks),1):
            if n % 100 == 0:
                print(f'TÉMOIN : {n}/{len(tasks)} vérifiés', flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(collector.departement,args.deps))


def preparer_cibles(args):
    geography = json.loads((args.cache/'communes-reference.json').read_text())
    tasks, report = [], {}
    for dep in args.deps:
        inventory = json.loads((args.cache/'departements'/(dep+'.json')).read_text())
        companies = inventory['entreprises']
        witnessed = {}
        for p in (args.cache/'temoin'/dep).glob('*.json'):
            for c in json.loads(p.read_text())['entreprises']:
                witnessed[c['siren']]=c
        selected=[]
        for siren,c in dict(companies,**witnessed).items():
            c = companies.get(siren,c)
            # Un compte national (même égal au cache) ne prouve rien pour ce
            # département. Aucun site d'un autre département ne compense une
            # omission locale. Le témoin stock permet ensuite de cibler par SIRET.
            possible = c['incomplet_possible'] or siren in witnessed
            if possible:
                selected.append(c)
        selected.sort(key=lambda c:(c['siren'] not in witnessed,-(c['ouverts_nationaux'] or 0),c['siren']))
        codes=[c for c in geography if c.startswith(dep)]
        for generic,prefix,n in [('75056','751',20),('69123','6938',9),('13055','132',16)]:
            if generic in codes:
                codes.remove(generic)
                codes.extend(prefix+str(i).zfill(5-len(prefix)) for i in range(1,n+1))
        codes=sorted(set(codes))
        if not codes:raise ValueError('Référentiel de communes absent : '+dep)
        tasks.extend((dep,c,codes) for c in selected)
        report[dep]=dict(entreprises=len(companies),alertes_departement=sum(c['incomplet_possible'] for c in companies.values()),
                         cibles=len(selected),communes=len(codes),temoin_entreprises=len(witnessed),
                         alertes_ecartees_par_compteur_national=0,
                         limite='Aucune alerte écartée par un compteur national. Le témoin stock compare les SIRET par département ; les compteurs API ne certifient pas la complétude.',
                         cibles_siren=[c['siren'] for c in selected])
    atomic_json(args.cache/'cibles.json',report)
    return tasks


def run_communes(collector,args):
    tasks=preparer_cibles(args)
    print('CIBLES : '+str(Counter(d for d,_,_ in tasks)),flush=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        for n,_ in enumerate(pool.map(collector.entreprise,tasks),1):
            if n%10==0:print(f'ENTREPRISES : {n}/{len(tasks)} examinées',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--donnees', type=Path, required=True)
    parser.add_argument('--deps', nargs='+', required=True)
    parser.add_argument('--phase', choices=['inventaire','cibles','communes'], required=True)
    args = parser.parse_args()
    allowed={d for a in json.loads((ROOT/'commun/academies.json').read_text()) for d in a['deps']}
    if set(args.deps)-allowed:
        parser.error('Département hors du périmètre des académies couvertes')
    configurer_cache(args.cache)
    with (args.cache/'verrou').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        collector = Rattrapage(args.cache,5)
        start, stamp = time.monotonic(), maintenant()
        try:
            if args.phase=='inventaire':run_inventory(collector,args)
            elif args.phase=='cibles':preparer_cibles(args)
            else:run_communes(collector,args)
        finally:
            value = dict(debut=stamp,fin=maintenant(),secondes=time.monotonic()-start,
                         requetes=collector.requests,erreurs=dict(collector.errors),phase=args.phase)
            atomic_json(args.cache/'executions'/(stamp.replace(':','-')+'.json'),value)
            print(json.dumps(value,ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
