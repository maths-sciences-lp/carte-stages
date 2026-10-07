"""Caches Onisep : curl, User-Agent navigateur, trois secondes entre fiches."""
import hashlib
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import time


def fiches(ids, sources, cache):
    dest = Path(cache)/'fiches'
    dest.mkdir(parents=True, exist_ok=True)
    journal = []
    previous = Path(cache)/'fiches-collecte.json'
    known = {r['id']: r for r in json.loads(previous.read_text())} if previous.exists() else {}
    for fid in sorted(set(ids)):
        p = dest/(fid+'.html')
        old = Path(sources)/'fiches'/p.name
        action = known.get(fid, {}).get('origine', 'cache national')
        if not p.exists() and old.exists():
            shutil.copy2(old, p)
            action = 'cache historique'
        elif not p.exists():
            url = 'https://www.onisep.fr/http/redirection/formation/slug/FOR.'+fid
            temp = p.with_suffix('.part')
            subprocess.run(['curl', '--fail', '--location', '--retry', '2', '--retry-delay', '3',
                            '--max-time', '90', '--silent', '--show-error', '-A', 'Mozilla/5.0',
                            '-o', str(temp), url], check=True)
            text = temp.read_text()
            if '<h1' not in text or 'onisep' not in text.lower():
                raise ValueError('Fiche Onisep inattendue : '+fid)
            temp.replace(p)
            action = 'téléchargée'
            print('Fiche '+fid+' téléchargée', flush=True)
            time.sleep(3)
        journal.append(dict(id=fid, origine=action, date=datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds'), sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (Path(cache)/'fiches-collecte.json').write_text(json.dumps(journal, ensure_ascii=False, indent=2)+'\n')
    return journal
