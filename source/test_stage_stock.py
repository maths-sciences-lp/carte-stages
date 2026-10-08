"""Le témoin doit reproduire les filtres de l'API, pas ceux de l'établissement."""
import importlib.util
import unittest
from stage_stock_comparer import creer_diagnostic


@unittest.skipUnless(importlib.util.find_spec('duckdb'), 'DuckDB dans le venv du pilote')
class StockTest(unittest.TestCase):
    def test_filtre_effectif_et_naf_sur_unite_legale(self):
        import duckdb
        c=duckdb.connect()
        c.execute("CREATE TABLE codes AS SELECT '43.22B' AS code")
        c.execute("CREATE TABLE effectifs AS SELECT '01' AS code")
        c.execute('CREATE TABLE e(siret VARCHAR,siren VARCHAR,etatAdministratifEtablissement VARCHAR,statutDiffusionEtablissement VARCHAR,activitePrincipaleEtablissement VARCHAR,trancheEffectifsEtablissement VARCHAR)')
        c.execute('CREATE TABLE u(siren VARCHAR,etatAdministratifUniteLegale VARCHAR,activitePrincipaleUniteLegale VARCHAR,trancheEffectifsUniteLegale VARCHAR,categorieJuridiqueUniteLegale VARCHAR,statutDiffusionUniteLegale VARCHAR)')
        c.executemany('INSERT INTO e VALUES (?,?,?,?,?,?)',[
            ('A1','A','A','O','00.00Z','NN'),
            ('B1','B','A','O','43.22B','01'),
            ('C1','C','A','O','43.22B','01'),
            ('D1','D','A','P','43.22B','01'),
            ('E1','E','F','O','43.22B','01'),
            ('F1','F','A','O','43.22B','01'),
        ])
        c.executemany('INSERT INTO u VALUES (?,?,?,?,?,?)',[
            ('A','A','43.22B','01','5710','O'),
            ('B','A','43.22B','NN','5710','O'),
            ('C','A','43.22B','01','1000','O'),
            ('D','A','43.22B','01','5710','O'),
            ('E','A','43.22B','01','5710','O'),
        ])
        creer_diagnostic(c)
        self.assertEqual(dict(c.execute('SELECT siret,motif FROM diagnostic').fetchall()),{
            'A1':'candidat','B1':'effectif_hors_liste','C1':'entrepreneur_individuel',
            'D1':'non_diffusible','E1':'ferme','F1':'unite_absente'})
        c.close()


class SelectionTest(unittest.TestCase):
    def test_comparaison_siret_par_departement_sans_compensation(self):
        from stage_stock_preparer import selectionner
        candidates={('75','A'):{'A1','A2'},('92','A'):{'A3'},('75','B'):{'B1','B2'}}
        published={'75':{'A1','B1','B2'},'92':{'A2','A3'}}
        pop,sample=selectionner(candidates,published,{'A','B'},2,20261009)
        self.assertEqual({(x['departement'],x['siren']) for x in pop},{('92','A'),('75','B')})
        self.assertEqual(sample,selectionner(candidates,published,{'A','B'},2,20261009)[1])

    def test_seuil_disque(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from stage_stock_config import espace_libre
        with patch('stage_stock_config.shutil.disk_usage',return_value=SimpleNamespace(free=1_999_999_999)):
            with self.assertRaises(RuntimeError):espace_libre('.')

    def test_descriptions_historiques_ne_deviennent_pas_des_ajouts(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from stage_collecte import atomic_json
        from stage_ajouts import candidats
        with TemporaryDirectory() as tmp:
            cache=Path(tmp)
            atomic_json(cache/'configuration-stock.json',{})
            atomic_json(cache/'departements/75.json',dict(rows=[{'s':'ancien'}]))
            self.assertEqual(candidats(cache,['75'])[0],{'75':{}})

class PartialReaderTest(unittest.TestCase):
    def test_relais_refuse_un_telechargement_complet(self):
        import http.client
        from http.server import ThreadingHTTPServer
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import threading
        from unittest.mock import patch
        from stage_stock_temoin import PartialReader
        with TemporaryDirectory() as tmp:
            reader=PartialReader(Path(tmp),10_000_000)
            server=ThreadingHTTPServer(('127.0.0.1',0),reader.handler())
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                with patch('stage_stock_temoin.urllib.request.urlopen') as remote:
                    conn=http.client.HTTPConnection('127.0.0.1',server.server_port)
                    conn.request('GET','/etablissements.parquet')
                    response=conn.getresponse();self.assertEqual(response.status,400);response.read();conn.close()
                    conn=http.client.HTTPConnection('127.0.0.1',server.server_port)
                    conn.request('GET','/etablissements.parquet',headers={'Range':'bytes=0-10000000'})
                    response=conn.getresponse();self.assertEqual(response.status,413);response.read();conn.close()
                    remote.assert_not_called()
            finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
