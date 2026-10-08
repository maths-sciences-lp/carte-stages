"""Régressions de la collecte : compteurs, filtres directs, reprise et 429."""
from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import contextlib
import io
from stage_collecte import Collector, couverture, attente_retry
from stage_rattrapage import admissible, Rattrapage, preparer_cibles
from stage_ajouts import ajouter_lignes, candidats, verifier_fin_pilote


def company(opened=3):
    return dict(siren='123456789',nom_complet='ENTREPRISE TEST',nature_juridique='5710',
                statut_diffusion='O',etat_administratif='A',activite_principale='43.22B',
                tranche_effectif_salarie='01',nombre_etablissements_ouverts=opened,
                matching_etablissements=[dict(siret='12345678900011',commune='93006',
                etat_administratif='A',statut_diffusion_etablissement='O',latitude='48.87',
                longitude='2.43',activite_principale='43.22B',adresse='1 rue Test')])


class RecoveryTest(unittest.TestCase):
    def test_le_stock_ne_permet_pas_ecriture_avant_sondage_et_controles(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            (d/'stock-verification-resultats.json').write_text('{"terminee":true}')
            (d/'stock-verifications-attendues.json').write_text('{"controles":[{"dep":"93","siret":"12345678900011"}]}')
            with self.assertRaisesRegex(ValueError,'SIRET absents'):verifier_fin_pilote(d,['93'])
            (d/'stock-api/temoin/93').mkdir(parents=True)
            (d/'stock-api/temoin/93/12345678900011.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'sondage absent'):verifier_fin_pilote(d,['93'])
            (d/'sondage-resultats.json').write_text('{"echantillon":100,"selection_a_elargir":true}')
            with self.assertRaisesRegex(ValueError,'sondage à reprendre'):verifier_fin_pilote(d,['93'])

    def test_un_compteur_national_ne_compense_pas_un_site_local_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory);(d/'departements').mkdir()
            (d/'communes-reference.json').write_text(json.dumps(['93006']))
            (d/'nombres-nationaux-temoin.json').write_text(json.dumps({'123456789':500}))
            (d/'departements/93.json').write_text(json.dumps({'entreprises':{'123456789':couverture(company(3),'93')}}))
            targets=preparer_cibles(SimpleNamespace(cache=d,deps=['93']))
            self.assertEqual([x[1]['siren'] for x in targets],['123456789'])

    def test_compteur_approximatif_seul_ne_declenche_pas_des_requetes_sans_fin(self):
        with tempfile.TemporaryDirectory() as directory:
            c=Collector(Path(directory),5)
            result=dict(total=2,pages=1,rows=[],exclusions={},unites=['a'],entreprises=[],collected_at='2026-10-08')
            with patch('stage_collecte.CODES',['A']),patch('stage_collecte.EFFECTIFS',['01']),patch.object(c,'page',return_value=result) as get,contextlib.redirect_stdout(io.StringIO()):
                c.departement('93')
                self.assertEqual(get.call_count,1)
                self.assertEqual(len(list((Path(directory)/'ecarts-compteur/93').glob('*.json'))),1)

    def test_ecriture_refusee_tant_qu_un_controle_cible_manque(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            (d/'cibles.json').write_text(json.dumps({'93':{'cibles_siren':['123456789']}}))
            (d/'temoin-attendu.json').write_text(json.dumps({'93':['12345678900011']}))
            with self.assertRaisesRegex(ValueError,'incomplet'):
                verifier_fin_pilote(d,['93'])
            (d/'entreprises/93').mkdir(parents=True);(d/'temoin/93').mkdir(parents=True)
            (d/'entreprises/93/123456789.json').write_text('{}')
            (d/'temoin/93/12345678900011.json').write_text('{}')
            verifier_fin_pilote(d,['93'])

    def test_rejet_individuel_interdit_un_ajout_trouve_dans_un_lot(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory);(d/'departements').mkdir();(d/'temoin/93').mkdir(parents=True)
            (d/'departements/93.json').write_text(json.dumps({'rows':[{'s':'12345678900011'}]}))
            (d/'temoin/93/12345678900011.json').write_text(json.dumps({'siret':'12345678900011','rows':[],'rejets':{'ferme':1}}))
            rows,_=candidats(d,['93']);self.assertEqual(rows,{'93':{}})
    def test_ajouts_preservent_ordre_valeurs_et_siret_existants(self):
        old=[['Ancien','','',48.8,2.4,1,0,'12345678900011','']]
        changed=[['Autre nom','','',48.9,2.5,3,0,'12345678900011','']]
        new=[['Nouveau','','',48.7,2.3,1,0,'12345678900029','']]
        after=ajouter_lignes(old,changed+new+new)
        self.assertEqual(after,old+new)
        self.assertEqual(ajouter_lignes(after,new),after)
    def test_compteur_global_est_une_alerte_pas_un_deficit_certain(self):
        c=couverture(company(), '93')
        self.assertTrue(c['incomplet_possible'])
        self.assertEqual(len(c['ouverts_recus_departement']),1)
        self.assertFalse(couverture(company(1),'93')['incomplet_possible'])

    def test_plus_de_requete_q_siren_pour_fausse_page_suivante(self):
        h=company(200);h['matching_etablissements']*=100
        with tempfile.TemporaryDirectory() as d:
            c=Collector(Path(d),5)
            with patch.object(c,'get',return_value=dict(total_results=1,total_pages=1,results=[h])) as get:
                value=c.page('93',['43.22B'],['01'],1)
                self.assertEqual(get.call_count,1)
                self.assertTrue(value['entreprises'][0]['liste_saturee'])

    def test_requete_directe_reapplique_filtres_unite_et_etablissement(self):
        h=company();e=h['matching_etablissements'][0]
        self.assertIsNotNone(admissible(h,e,'93',Counter()))
        for field,value in [('etat_administratif','C'),('activite_principale','00.00Z'),('tranche_effectif_salarie','NN'),('nature_juridique','1000'),('statut_diffusion','P')]:
            with self.subTest(field=field):
                self.assertIsNone(admissible(dict(h,**{field:value}),e,'93',Counter()))
        for field,value in [('etat_administratif','F'),('commune','75056'),('latitude',None),('statut_diffusion_etablissement','P')]:
            self.assertIsNone(admissible(h,dict(e,**{field:value}),'93',Counter()))

    def test_siret_exact_et_reprise_sans_nouvelle_requete(self):
        with tempfile.TemporaryDirectory() as d:
            c=Rattrapage(Path(d),5)
            with patch.object(c,'get',return_value=dict(results=[company()])) as get:
                first=c.verifier_siret(('93','12345678900011'))
                self.assertEqual(c.verifier_siret(('93','12345678900011')),first)
                self.assertEqual(get.call_count,1)
                self.assertEqual(len(first['rows']),1)
                wrong=c.verifier_siret(('93','12345678999999'))
                self.assertEqual(wrong['rejets'],{'siret_introuvable':1})

    def test_retry_after(self):
        self.assertEqual(attente_retry('65',5),65)
        self.assertEqual(attente_retry(None,5),5)

    def test_lot_avec_doublons_est_redecoupe(self):
        with tempfile.TemporaryDirectory() as d:
            c=Collector(Path(d),5)
            def page(dep,codes,eff,num):
                bad=len(codes)>1
                return dict(total=2 if bad else 1,pages=1,page=1,rows=[],exclusions={},
                            unites=['a','a'] if bad else [codes[0]],entreprises=[],collected_at='2026-10-08')
            with patch('stage_collecte.CODES',['A','B']),patch('stage_collecte.EFFECTIFS',['01']),patch.object(c,'page',side_effect=page) as get,contextlib.redirect_stdout(io.StringIO()):
                c.departement('93')
                self.assertEqual(get.call_count,3)

    def test_gros_lot_est_decoupe_avant_telechargement_complet(self):
        with tempfile.TemporaryDirectory() as d:
            c=Collector(Path(d),5)
            def page(dep,codes,eff,num):
                return dict(total=3000 if len(codes)>1 else 1,pages=120 if len(codes)>1 else 1,
                            rows=[],exclusions={},unites=[codes[0]],entreprises=[],collected_at='2026-10-08')
            with patch('stage_collecte.CODES',['A','B']),patch('stage_collecte.EFFECTIFS',['01']),patch.object(c,'page',side_effect=page) as get,contextlib.redirect_stdout(io.StringIO()):
                c.departement('93')
                self.assertEqual(get.call_count,3)

    def test_recuperation_commune_meme_si_parent_recoit_moins_de_cent(self):
        with tempfile.TemporaryDirectory() as d:
            c=Rattrapage(Path(d),5)
            def group(dep,h,codes):
                # Le lot large omet le second établissement, sans atteindre 100.
                rows=([{'s':'12345678900011'}] if '93006' in codes else
                      [{'s':'12345678900029'}] if '93007' in codes else [])
                return dict(rows=rows,rejets={},trouve=bool(rows),incertain=None)
            with patch.object(c,'groupe_communes',side_effect=group) as get:
                found=c.entreprise(('93',couverture(company(),'93'),['93006','93007','93008','93009']))
                self.assertEqual({r['s'] for r in found['rows']},{'12345678900011','12345678900029'})
                calls=get.call_count
                self.assertEqual(c.entreprise(('93',couverture(company(),'93'),['93006','93007','93008','93009'])),found)
                self.assertEqual(get.call_count,calls)

    def test_nom_homonyme_ne_permet_pas_ajout_et_siren_ne_desactive_pas_geo(self):
        with tempfile.TemporaryDirectory() as d:
            c=Rattrapage(Path(d),5)
            wrong=company();wrong['siren']='999999999'
            with patch.object(c,'get',return_value=dict(results=[wrong],total_results=1,total_pages=1)) as get:
                r=c.groupe_communes('93',couverture(company(),'93'),['93006'])
                self.assertFalse(r['trouve']);self.assertEqual(r['rows'],[])
                self.assertEqual(get.call_args.args[0]['q'],'ENTREPRISE TEST')
                self.assertEqual(get.call_args.args[0]['code_commune'],'93006')


if __name__=='__main__':unittest.main()
