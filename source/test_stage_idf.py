"""Contrats durables : alias historiques, manifestes, frontières et ajout sans retrait."""
import gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from stage_catalogues import ecrire_catalogues,IDF,LIMITROPHES
from stage_donnees import catalogue_formations
ROOT=Path(__file__).resolve().parents[1]
class MigrationTest(unittest.TestCase):
    def test_alias_reproduisent_premiere_option_historique(self):
        old=json.loads((ROOT/'data/index.json').read_text());new=catalogue_formations();aliases=json.loads((ROOT/'stage/aliases-idf.json').read_text());seen=set()
        for f in old['formations']:
            if f['k'] in seen:continue
            seen.add(f['k']);n=next(n for n in new['formations'] if n['k']==aliases.get(f['k'],f['k']))
            # « Écoles maternelles et élémentaires » est dérivée des mairies (audit du 8/10/2026).
            self.assertEqual((n['n'],[x for x in n['s'] if x!='ecoles-maternelles-et-elementaires']),(f['n'],f['s']))
        self.assertEqual(len(seen),180);self.assertEqual(len(aliases),4)
    def test_manifeste_differe_et_departements_limitrophes(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);cat={'academies':[{'deps':IDF}], 'domaines':[{'s':[{'k':'a','c':50}]}], 'departements':{d:{'secteurs':{'a':{'n':2,'sha256':'abc'}},'bbox':[0,0,1,1]} for d in IDF+LIMITROPHES+['59']}}
            (p/'catalogue.json').write_text(json.dumps(cat));ecrire_catalogues(p)
            lite=json.loads((p/'catalogues/ile-de-france.json').read_text())
            self.assertEqual(set(lite['departements']),set(IDF+LIMITROPHES));self.assertEqual(lite['domaines'][0]['s'][0]['c'],16)
            for d,meta in lite['departements'].items():
                self.assertNotIn('secteurs',meta);self.assertEqual(meta['manifeste'],hashlib.sha256((p/'manifestes'/f'{d}.json').read_bytes()).hexdigest())
    def test_apercu_regional_sans_catalogue_idf_trompeur(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);cat={'academies':[], 'domaines':[], 'departements':{'69':{'secteurs':{},'bbox':[0,0,1,1]}}}
            (p/'catalogue.json').write_text(json.dumps(cat))
            sizes=ecrire_catalogues(p)
            self.assertIn('catalogue-leger.json',sizes)
            self.assertFalse((p/'catalogues/ile-de-france.json').exists())
if __name__=='__main__':unittest.main()
