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
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = Path.home() / 'Library/Application Support/carte-stages/lba-api-key'
EXPORT_API = 'https://api.apprentissage.beta.gouv.fr/api/job/v1/export'


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
    idx = json.loads((root / 'data/index.json').read_text())
    paths = {s['k'] for d in idx['domaines'] for s in d['s']}
    return {str(r[7]) for k in paths
            for r in json.loads((root / 'data' / (k + '.json')).read_text())
            if len(r) > 7 and re.fullmatch(r'\d{14}', str(r[7]))}


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
            jobs.append(dict(title=offer['title'], url=url, expiration=expiration,
                             romes=offer.get('rome_codes') or [],
                             diploma=diploma.get('european')))
    return companies, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true', help='Écrire data/lba-index.json.')
    parser.add_argument('--input', type=Path, help='Analyser un export JSON local, sans API.')
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    allowed = catalogue(args.root)
    print(f'{len(allowed)} SIRET existants ; aucune nouvelle entreprise ajoutée.', flush=True)
    if args.input:
        stream = args.input.open(encoding='utf-8')
        updated = now.isoformat()
    else:
        key = os.environ.get('LBA_API_KEY') or KEY_FILE.read_text().strip()
        req = urllib.request.Request(EXPORT_API, headers={'Authorization': 'Bearer ' + key})
        with urllib.request.urlopen(req, timeout=30) as response:
            info = json.load(response)
        url = safe_url(info.get('url'))
        if not url or timestamp(info.get('lastUpdate')) is None:
            raise ValueError('Réponse export invalide.')
        updated = info['lastUpdate']
        # L'URL de téléchargement signée est éphémère ; ne pas la journaliser.
        stream = io.TextIOWrapper(urllib.request.urlopen(url, timeout=60), encoding='utf-8')
    with stream:
        companies, counts = enrich(records(stream), allowed, now)
    if counts['opportunities'] == 0:
        raise ValueError('Export vide : conserver le dernier enrichissement.')
    result = dict(source='La Bonne Alternance', updated_at=updated,
                  retrieved_at=now.isoformat(), max_age_days=7,
                  companies=dict(sorted(companies.items())), counts=counts)
    print(json.dumps(dict(counts, matched_companies=len(companies)), ensure_ascii=False), flush=True)
    if not args.write:
        print('Dry-run : aucun fichier modifié.')
        return
    target = args.root / 'data/lba-index.json'
    fd, tmp = tempfile.mkstemp(prefix='lba-', suffix='.tmp', dir=target.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
            f.write('\n')
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print('Écrit : data/lba-index.json', flush=True)


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        sys.exit(f'API indisponible : HTTP {error.code}. Aucun fichier publié remplacé.')
    except Exception as error:
        # Ne jamais inclure les URL signées ou le jeton dans une erreur.
        sys.exit(f'Échec ({type(error).__name__}) : aucun fichier publié remplacé.')
