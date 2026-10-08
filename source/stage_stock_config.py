"""Configuration immuable d'un rattrapage départemental, jamais national implicite."""
import json
import hashlib
from pathlib import Path
import shutil


def configuration(cache):
    path = Path(cache)/'configuration-stock.json'
    if path.exists():
        from stage_collecte import CODES
        cfg=json.loads(path.read_text())
        if cfg.get('empreinte_naf')!=hashlib.sha256('\n'.join(CODES).encode()).hexdigest():
            raise ValueError('Les codes NAF ont changé depuis la préparation du cache')
        return cfg
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
