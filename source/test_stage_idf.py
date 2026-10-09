"""Contrats durables : alias historiques, manifestes, frontières et ajout sans retrait."""
import gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from stage_catalogues import ecrire_catalogues,IDF,LIMITROPHES
from stage_donnees import catalogue_formations,slug
from domaines import DECOUPAGES
origine={slug(k):slug(v) for k,v in DECOUPAGES.items()}
ROOT=Path(__file__).resolve().parents[1]
class MigrationTest(unittest.TestCase):
    def test_alias_reproduisent_premiere_option_historique(self):
        old=json.loads((ROOT/'data/index.json').read_text());new=catalogue_formations();aliases=json.loads((ROOT/'stage/aliases-idf.json').read_text());seen=set()
        for f in old['formations']:
            if f['k'] in seen:continue
            seen.add(f['k']);n=next(n for n in new['formations'] if n['k']==aliases.get(f['k'],f['k']))
            # Catégories découpées depuis 2026-10 (écoles, réseaux…) : ramenées à leur origine ;
            # routes de l'État (9/10/2026) : ajoutées au géomètre et aux travaux publics, ignorées ici,
            # comme les types copiés (hôpitaux avec service technique, bailleurs sociaux) et la promotion
            # immobilière, nouveau type du TEB études et économie et de sa 2de EMNB, carrières et démolition
            # (conducteur d'engins, travaux publics, gros œuvre, maintenance des matériels de construction).
            # Ajouts voulus : la 2de TNE reçoit aussi les entreprises du bac pro CIEL (8/10/2026) ;
            # l'ERA, les architectes et le design d'intérieur (bureau d'études, 9/10/2026).
            ajouts=['services-informatiques-reseaux','reparation-d-ordinateurs-et-de-telephones','electronique-materiel-electrique'] if 'tne' in n['k'] else \
                   ['architectes','publicite-design-graphique'] if n['k']=="bac-pro-etude-et-realisation-d-agencement" else []
            # Retraits voulus : réparateurs de machines (CAP monteur), ingénierie 71.12B (géomètre),
            # syndics et bailleurs sans équipe technique (CAP IMTB, 9/10/2026).
            retraits={'cap-monteur-en-installations-thermiques':['maintenance-d-equipements-ascenseurs'],
                      'bac-pro-geometre':['bureaux-d-etudes-economistes-de-la-construction'],
                      'cap-interventions-en-maintenance-technique-des-batiments':['agences-immobilieres-gestion-de-logements']}.get(n['k'],[])
            self.assertEqual((n['n'],list(dict.fromkeys(origine.get(x,x) for x in n['s'] if not x.startswith('routes-de-l-etat') and x not in ('hopitaux-services-techniques', 'bailleurs-sociaux', 'promotion-immobiliere', 'carrieres', 'demolition',
                   'lycees-publics-maintenance', 'colleges-publics-maintenance')))),(f['n'],[x for x in f['s'] if x not in retraits]+ajouts))
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
