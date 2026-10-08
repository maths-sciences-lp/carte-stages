"""Enrichit le dépôt national séparé ; --idf-root prépare aussi la mise à jour IDF.

Un seul export LBA est analysé. Aucun export brut, jeton ou contact personnel
n'est enregistré. Sans --write : lecture et bilan uniquement.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from lba import (catalogue, enrich, records, ouvrir_export,
                 RECRUITER_MAX_AGE, OFFER_MAX_AGE)


def catalogue_national(root):
    index = json.loads((root/'catalogue.json').read_text())
    if index.get('schema') != 1 or not index.get('complet'):
        raise ValueError('Le catalogue national doit être complet et validé')
    allowed = defaultdict(set)
    for dep, data in index['departements'].items():
        if not re.fullmatch(r'(?:\d{2,3}|2[AB])', dep):
            raise ValueError('Département invalide')
        for sector, info in data['secteurs'].items():
            if not re.fullmatch(r'[a-z0-9-]+', sector):
                raise ValueError('Secteur invalide')
            raw = (root/'sirene'/dep/(sector+'.json')).read_bytes()
            if hashlib.sha256(raw).hexdigest() != info['sha256']:
                raise ValueError('Fichier Sirene différent du catalogue')
            rows = json.loads(raw)
            if len(rows) != info['n']:
                raise ValueError('Nombre d’établissements incohérent')
            for row in rows:
                siret = str(row[7])
                if not re.fullmatch(r'\d{14}', siret):
                    raise ValueError('SIRET invalide')
                allowed[siret].add(dep+'/'+sector)
    return dict(allowed)


def preparer_dossier(target, allowed, companies, meta, national=False):
    """Écrit et vérifie un dossier temporaire sans toucher aux derniers fichiers."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.lba-preparation-', dir=target.parent))
    try:
        groups = defaultdict(dict)
        for siret, entry in companies.items():
            for key in allowed.get(siret, ()):
                groups[key][siret] = entry
        files = defaultdict(list)
        for key, entries in sorted(groups.items()):
            path = temp/(key+'.json')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(dict(sorted(entries.items())), ensure_ascii=False, separators=(',', ':'))+'\n')
            if national:
                dep, sector = key.split('/')
                files[dep].append(sector)
        metadata = dict(meta, matched_companies=sum(s in allowed for s in companies), sectors=len(groups))
        if national:
            metadata.update(schema=1, files=dict(files))
        (temp/'meta.json').write_text(json.dumps(metadata, ensure_ascii=False, separators=(',', ':'))+'\n')
        for path in temp.rglob('*'):
            os.chmod(path, 0o755 if path.is_dir() else 0o644)
            if path.is_file():
                json.loads(path.read_text())
        os.chmod(temp, 0o755)
        return temp
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        raise


def remplacer_dossiers(pairs):
    """Restaure les versions précédentes si un remplacement échoue.

    La mise à jour mensuelle appelle ceci dans des copies temporaires : un arrêt
    brutal de la machine ne peut donc pas toucher aux fichiers servis.
    """
    backups, installed = [], []
    try:
        for temp, target in pairs:
            backup = temp.with_name(temp.name+'-precedent')
            if target.exists():
                os.replace(target, backup)
                backups.append((backup, target))
            os.replace(temp, target)
            installed.append(target)
    except BaseException:
        for target in reversed(installed):
            shutil.rmtree(target)
        for backup, target in reversed(backups):
            os.replace(backup, target)
        raise
    else:
        for backup, _ in backups:
            shutil.rmtree(backup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Copie du dépôt national de données')
    parser.add_argument('--idf-root', type=Path, help='Copie temporaire du dépôt du site, pour la mise à jour mensuelle')
    parser.add_argument('--input', type=Path, help='Export local de test, sans API')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    if root == Path(__file__).resolve().parents[1] or not (root/'.git').exists():
        parser.error('Le dépôt national de données doit être une copie Git séparée')
    national = catalogue_national(root)
    idf = catalogue(args.idf_root) if args.idf_root else {}
    allowed = national.keys() | idf.keys()
    print(f'{len(allowed)} SIRET existants ; aucune nouvelle entreprise ajoutée.', flush=True)
    now = datetime.now(timezone.utc)
    stream, updated = ouvrir_export(args.input, now)
    with stream:
        companies, counts = enrich(records(stream), allowed, now)
    if counts['opportunities'] == 0:
        raise ValueError('Export vide : conserver les derniers fichiers valides')
    if not any(s in national for s in companies) or (idf and not any(s in idf for s in companies)):
        raise ValueError('Aucun rapprochement dans un des catalogues : conserver les derniers fichiers valides')
    meta = dict(source='La Bonne Alternance', updated_at=updated, retrieved_at=now.isoformat(),
                recruiter_max_age_days=RECRUITER_MAX_AGE, offer_max_age_days=OFFER_MAX_AGE, counts=counts)
    print(json.dumps(dict(counts, matched_companies=len(companies)), ensure_ascii=False), flush=True)
    if not args.write:
        print('Dry-run : aucun fichier modifié.')
        return
    pairs = []
    try:
        target = root/'lba'
        pairs.append((preparer_dossier(target, national, companies, meta, True), target))
        if args.idf_root:
            target = args.idf_root.resolve()/'data/lba'
            pairs.append((preparer_dossier(target, idf, companies, meta), target))
        remplacer_dossiers(pairs)
    finally:
        for temp, _ in pairs:
            shutil.rmtree(temp, ignore_errors=True)
    print('Enrichissement préparé localement ; rien publié.', flush=True)
