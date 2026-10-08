#!/usr/bin/env python3
"""Enrichissement local LBA, limité aux SIRET déjà diffusés par la carte.

La clé n'est ni un argument de commande ni une donnée publiée. Sans --write,
le programme affiche seulement le bilan (dry-run).
"""
import argparse
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = Path.home() / 'Library/Application Support/carte-stages/lba-api-key'
EXPORT_API = 'https://api.apprentissage.beta.gouv.fr/api/job/v1/export'
# Durées d'affichage côté page : le badge « recruteur potentiel » évolue lentement,
# les offres ont leur propre date d'expiration (sinon masquées après 7 jours).
RECRUITER_MAX_AGE = 31
OFFER_MAX_AGE = 7


def records(stream):
    """Lire un tableau JSON sans charger l'export national en mémoire."""
    decoder = json.JSONDecoder()
    buf, pos, eof = '', 0, False

    def refill():
        nonlocal buf, pos, eof
        part = stream.read(65536)
        buf, pos = buf[pos:] + part, 0
        eof = not part

    def space():
        nonlocal pos
        while True:
            while pos < len(buf) and buf[pos].isspace():
                pos += 1
            if pos < len(buf) or eof:
                return
            refill()

    refill()
    space()
    if pos >= len(buf) or buf[pos] != '[':
        raise ValueError('Export attendu : tableau JSON.')
    pos += 1
    space()
    if pos < len(buf) and buf[pos] == ']':
        pos += 1
    else:
        while True:
            space()
            while True:
                try:
                    value, end = decoder.raw_decode(buf, pos)
                    break
                except json.JSONDecodeError:
                    if eof:
                        raise ValueError('Export JSON incomplet ou invalide.') from None
                    refill()
            if not isinstance(value, dict):
                raise ValueError('Une opportunité doit être un objet JSON.')
            pos = end
            yield value
            space()
            if pos >= len(buf):
                raise ValueError('Export JSON incomplet.')
            delimiter = buf[pos]
            pos += 1
            if delimiter == ']':
                break
            if delimiter != ',':
                raise ValueError('Séparateur JSON invalide.')
    space()
    if pos < len(buf):
        raise ValueError('Contenu inattendu après le tableau JSON.')


def timestamp(value):
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)
    except (TypeError, ValueError, AttributeError):
        return None


def safe_url(value):
    if not isinstance(value, str):
        return None
    try:
        u = urllib.parse.urlsplit(value)
        if u.scheme == 'https' and u.hostname and not u.username and not u.password:
            return value
    except ValueError:
        pass
    return None


def catalogue(root):
    """SIRET déjà affichés par la carte -> secteurs (fichiers data/<secteur>.json) où ils figurent."""
    idx = json.loads((root / 'data/index.json').read_text())
    paths = {s['k'] for d in idx['domaines'] for s in d['s']}
    out = {}
    for k in sorted(paths):
        for r in json.loads((root / 'data' / (k + '.json')).read_text()):
            if len(r) > 7 and re.fullmatch(r'\d{14}', str(r[7])):
                out.setdefault(str(r[7]), set()).add(k)
    return out


def enrich(rows, allowed, now):
    companies, seen_jobs = {}, set()
    counts = dict(opportunities=0, recruiters=0, jobs=0, delegated_skipped=0)
    for item in rows:
        counts['opportunities'] += 1
        if counts['opportunities'] % 100000 == 0:
            print(f"{counts['opportunities']} opportunités analysées…", flush=True)
        if item.get('is_delegated'):
            counts['delegated_skipped'] += 1
            continue
        siret = str((item.get('workplace') or {}).get('siret') or '')
        if siret not in allowed:
            continue
        url = safe_url((item.get('apply') or {}).get('url'))
        if not url:
            continue
        ident = item.get('identifier') or {}
        source = ident.get('partner_label')
        if source == 'recruteurs_lba':
            # Ce signal n'est pas une preuve de recrutement ou d'accueil en PFMP.
            companies.setdefault(siret, {})['recruiter'] = url
            counts['recruiters'] += 1
            continue
        offer = item.get('offer') or {}
        diploma = offer.get('target_diploma') or {}
        if diploma.get('european') not in (None, '3', '4'):
            continue
        if offer.get('status') != 'Active':
            continue
        expiration = (offer.get('publication') or {}).get('expiration')
        until = timestamp(expiration) if expiration else None
        if expiration and (until is None or until <= now):
            continue
        if not offer.get('title'):
            continue
        job_id = (siret, url)
        if job_id in seen_jobs:
            continue
        seen_jobs.add(job_id)
        jobs = companies.setdefault(siret, {}).setdefault('jobs', [])
        counts['jobs'] += 1
        # Au plus trois liens par entreprise, sans CV ni coordonnées personnelles.
        if len(jobs) < 3:
            jobs.append(dict(title=offer['title'], url=url, expiration=expiration))
    return companies, counts


def ouvrir_export(input_path, now):
    """Un seul export national ; le jeton et l'URL signée restent en mémoire."""
    if input_path:
        return input_path.open(encoding='utf-8'), now.isoformat()
    key = os.environ.get('LBA_API_KEY') or KEY_FILE.read_text().strip()
    req = urllib.request.Request(EXPORT_API, headers={'Authorization': 'Bearer ' + key})
    with urllib.request.urlopen(req, timeout=30) as response:
        info = json.load(response)
    url = safe_url(info.get('url'))
    if not url or timestamp(info.get('lastUpdate')) is None:
        raise ValueError('Réponse export invalide.')
    return io.TextIOWrapper(urllib.request.urlopen(url, timeout=60), encoding='utf-8'), info['lastUpdate']


def main():
    if '--national' in sys.argv:
        sys.argv.remove('--national')
        from stage_lba import main as national
        return national()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true', help='Écrire data/lba/ (un fichier par secteur).')
    parser.add_argument('--input', type=Path, help='Analyser un export JSON local, sans API.')
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    allowed = catalogue(args.root)
    print(f'{len(allowed)} SIRET existants ; aucune nouvelle entreprise ajoutée.', flush=True)
    stream, updated = ouvrir_export(args.input, now)
    with stream:
        companies, counts = enrich(records(stream), allowed, now)
    if counts['opportunities'] == 0:
        raise ValueError('Export vide : conserver le dernier enrichissement.')
    meta = dict(source='La Bonne Alternance', updated_at=updated, retrieved_at=now.isoformat(),
                recruiter_max_age_days=RECRUITER_MAX_AGE, offer_max_age_days=OFFER_MAX_AGE, counts=counts)
    par_secteur = {}
    for siret, entry in companies.items():
        for k in allowed[siret]:
            par_secteur.setdefault(k, {})[siret] = entry
    print(json.dumps(dict(counts, matched_companies=len(companies), sectors=len(par_secteur)), ensure_ascii=False), flush=True)
    if not args.write:
        print('Dry-run : aucun fichier modifié.')
        return
    # Écriture dans un dossier temporaire, puis remplacement d'un bloc : jamais de mélange ancien/nouveau.
    target = args.root / 'data/lba'
    tmp = Path(tempfile.mkdtemp(prefix='lba-', dir=args.root / 'data'))
    try:
        for k, entries in par_secteur.items():
            (tmp / (k + '.json')).write_text(json.dumps(dict(sorted(entries.items())), ensure_ascii=False, separators=(',', ':')) + '\n')
        (tmp / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + '\n')
        for f in tmp.iterdir():
            os.chmod(f, 0o644)
        os.chmod(tmp, 0o755)
        old = args.root / 'data/lba.old'
        if target.exists():
            os.replace(target, old)
        os.replace(tmp, target)
        shutil.rmtree(old, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'Écrit : data/lba/ ({len(par_secteur)} secteurs + meta.json)', flush=True)


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        sys.exit(f'API indisponible : HTTP {error.code}. Aucun fichier publié remplacé.')
    except Exception as error:
        # Ne jamais inclure les URL signées ou le jeton dans une erreur.
        sys.exit(f'Échec ({type(error).__name__}) : aucun fichier publié remplacé.')
