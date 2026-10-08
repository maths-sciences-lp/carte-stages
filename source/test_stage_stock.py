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


if __name__=='__main__':unittest.main()
