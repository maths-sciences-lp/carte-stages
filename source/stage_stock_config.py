"""Configuration immuable d'un rattrapage départemental, jamais national implicite."""
import json
from pathlib import Path
import shutil


def configuration(cache):
    path = Path(cache)/'configuration-stock.json'
    if path.exists():
        return json.loads(path.read_text())
    return {'departements':['77','93','94'], 'date_stock':'2026-10-01', 'suffixe':'creteil'}


def departements(cache):
    return configuration(cache)['departements']


def extrait(cache, phase):
    return Path(cache)/('stock-'+phase+'-'+configuration(cache)['suffixe']+'.parquet')


def espace_libre(path, marge=0):
    path=Path(path)
    while not path.exists(): path=path.parent
    free=shutil.disk_usage(path).free
    if free < 2_000_000_000+marge:
        raise RuntimeError('Arrêt propre : espace libre insuffisant pour conserver 2 Go')
    return free
