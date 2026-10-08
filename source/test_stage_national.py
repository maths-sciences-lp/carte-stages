"""Contrôles hors réseau : catalogue complet, export LBA et conservation sur échec.

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s source -p test_stage_national.py
"""
from collections import Counter
from datetime import datetime, timezone
import io
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lba import enrich, records
from stage_donnees import ROOT, catalogue_formations, preparer, slug, verifier_cache
from stage_lba import preparer_dossier, remplacer_dossiers
from stage_collecte import configurer_cache


class NationalTest(unittest.TestCase):
    def test_toutes_les_options_de_formation_sont_distinctes_et_relies(self):
        index = catalogue_formations()
        mapping = json.loads((ROOT/'source/formation_secteurs.json').read_text())
        forms = {f['k']: f for f in index['formations']}
        self.assertEqual(len(forms), len(index['formations']))
        occurrences = Counter(slug(n) for n in mapping)
        for name, sectors in mapping.items():
            key = slug(name, None) if occurrences[slug(name)] > 1 else slug(name)
            self.assertEqual([x for x in forms[key]['s'] if x != 'ecoles-maternelles-et-elementaires'], [slug(s) for s in sectors], name)

    def test_ecoles_suivent_les_mairies_sauf_geometre_et_batiment(self):
        from domaines import ECOLES_EXCLUES
        for f in catalogue_formations()['formations']:
            attendu = 'mairies-administrations' in f['s'] and f['k'] not in ECOLES_EXCLUES
            self.assertEqual('ecoles-maternelles-et-elementaires' in f['s'], attendu, f['k'])
        self.assertEqual(len(ECOLES_EXCLUES), 5)

    def test_un_cache_ancien_est_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache/'configuration-collecte.json').write_text('{"codes_naf": [], "empreinte_naf": "ancien"}')
            with self.assertRaises(ValueError):
                verifier_cache(cache)

    def test_cache_neuf_reprenable_et_cache_inconnu_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)/'nouveau'
            configurer_cache(cache)
            before = (cache/'configuration-collecte.json').read_bytes()
            configurer_cache(cache)
            self.assertEqual((cache/'configuration-collecte.json').read_bytes(), before)
            verifier_cache(cache)
            inconnu = Path(directory)/'ancien'
            inconnu.mkdir()
            (inconnu/'page.json').write_text('{}')
            with self.assertRaises(ValueError):
                configurer_cache(inconnu)

    def test_etablissement_sans_nom_signale_et_non_publie(self):
        rows = [dict(n=None, nj='5499', du='O', de='O', la=45.0)]
        groups, excluded = preparer(rows)
        self.assertFalse(any(groups.values()))
        self.assertEqual(excluded, {'sans_nom': 1})

    def test_lieux_sans_personnel_retires_les_autres_gardes(self):
        def lieu(siret, c, q, nj):
            return dict(s=siret, n='LIEU ' + siret, e='', c=c, q=q, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj=nj, du='O', de='O', r=False)
        rows = [lieu('1', '42.99Z', '84.11Z', '7210'),   # lotissement communal
                lieu('2', '42.99Z', '42.99Z', '5710'),   # entreprise de génie civil
                lieu('3', '35.11Z', '01.41Z', '6533'),   # ferme avec panneaux solaires
                lieu('4', '35.11Z', '84.11Z', '7210'),   # panneaux solaires communaux
                lieu('5', '35.13Z', '84.11Z', '7210'),   # régie municipale d'électricité
                lieu('6', '42.22Z', '42.22Z', '5710')]   # réseaux électriques
        groups, excluded = preparer(rows)
        gardes = {r[7]: k for k, v in groups.items() for r in v}
        self.assertEqual(gardes, {'2': 'travaux-publics-routes-reseaux', '5': 'production-et-distribution-d-energie',
                                  '6': 'reseaux-electriques-et-telecoms'})
        self.assertEqual(excluded, {'sans_personnel': 3})

    def test_filiere_energie_tne_avec_ciel_et_electriciens_sans_routes(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        tne = forms['2nde-transitions-numerique-et-energetique-tne']
        for k in forms['bac-pro-cybersecurite-informatique-et-reseaux-electronique']:
            self.assertIn(k, tne)
        for k in ('2nde-transitions-numerique-et-energetique-tne', 'bac-pro-metiers-de-l-electricite-et-de-ses-environnements-co'):
            self.assertNotIn('travaux-publics-routes-reseaux', forms[k])
            self.assertIn('reseaux-electriques-et-telecoms', forms[k])
        # Ascenseurs découpés : électriciens / froid et climatisation / aucune réparation de machines.
        asc, froid, rep = 'maintenance-d-equipements-ascenseurs', 'froid-industriel-installation-de-machines', 'reparation-de-machines-et-d-electronique'
        for k in ('bac-pro-metiers-de-l-electricite-et-de-ses-environnements-co', 'cap-electricien'):
            self.assertEqual([x in forms[k] for x in (asc, froid, rep)], [True, False, False], k)
        for k in ('bac-pro-installateur-en-chauffage-climatisation-et-energies-', 'bac-pro-maintenance-et-efficacite-energetique',
                  'bac-pro-metiers-du-froid-et-des-energies-renouvelables', 'cap-installateur-en-froid-et-conditionnement-d-air'):
            self.assertEqual([x in forms[k] for x in (asc, froid, rep)], [False, True, False], k)
        self.assertFalse({asc, froid, rep} & set(forms['cap-monteur-en-installations-thermiques']))
        self.assertEqual([x in tne for x in (asc, froid, rep)], [True, True, False])
        # Hors de la filière, rien n'est perdu : les trois parties restent ensemble.
        for k in ('bac-pro-maintenance-des-systemes-de-production-connectes', 'cap-interventions-en-maintenance-technique-des-batiments'):
            self.assertTrue({asc, froid, rep} <= set(forms[k]), k)
        # Conseil en systèmes et logiciels (62.02A) retiré ; programmation et dépannage restent.
        from domaines import DOMAINES
        info = DOMAINES['Informatique, numérique, télécoms']['Services informatiques, réseaux']
        self.assertEqual(info, ['62.01Z', '62.03Z', '62.09Z'])
        # Les formations des travaux publics gardent tout : routes et réseaux.
        for k, s in forms.items():
            if 'travaux-publics-routes-reseaux' in s:
                self.assertIn('reseaux-electriques-et-telecoms', s, k)

    def test_filiere_batiment_communes_et_economistes(self):
        from domaines import ECOLES_EXCLUES
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        for k in ECOLES_EXCLUES:
            self.assertNotIn('mairies-administrations', forms[k], k)
            self.assertIn('communes-et-intercommunalites', forms[k], k)
        for k, s in forms.items():
            if 'mairies-administrations' in s:
                self.assertIn('communes-et-intercommunalites', s, k)
            if 'bureaux-d-etudes-economistes-de-la-construction' in s:
                self.assertIn('economistes-de-la-construction', s, k)
        self.assertNotIn('bureaux-d-etudes-economistes-de-la-construction', forms['bac-pro-geometre'])
        self.assertNotIn('bureaux-d-etudes-economistes-de-la-construction', forms['bac-pro-technicien-d-etudes-du-batiment-option-b-assistant-e'])
        def lieu(siret, c, q, nj):
            return dict(s=siret, n='LIEU ' + siret, e='', c=c, q=q, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj=nj, du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '84.11Z', '84.11Z', '7210'),   # mairie
                              lieu('2', '81.10Z', '84.11Z', '7210'),   # centre technique municipal
                              lieu('3', '84.24Z', '84.11Z', '7210'),   # gendarmerie communale
                              lieu('4', '84.11Z', '84.11Z', '7120'),   # service de l'État
                              lieu('5', '84.11Z', '84.11Z', '7346')])  # communauté de communes
        gardes = {r[7]: k for k, v in groups.items() for r in v}
        self.assertEqual(gardes, {'1': 'communes-et-intercommunalites', '2': 'communes-et-intercommunalites',
                                  '3': 'mairies-administrations', '4': 'mairies-administrations',
                                  '5': 'communes-et-intercommunalites'})

    def test_export_incomplet_refuse(self):
        for raw in ['[{"workplace": {}}', '[{},', '[] contenu inattendu']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                list(records(io.StringIO(raw)))

    def test_lba_exclusions_et_absence_contacts(self):
        now = datetime(2026, 10, 8, tzinfo=timezone.utc)
        siret = '12345678901234'
        base = dict(workplace=dict(siret=siret, email='personne@example.test'),
                    apply=dict(url='https://example.test/offre', phone='0100000000'),
                    offer=dict(status='Active', title='Offre test', target_diploma=dict(european='3')))
        rows = [dict(base, is_delegated=True),
                dict(base, workplace=dict(siret='99999999999999')),
                dict(base, apply=dict(url='javascript:alert(1)')),
                dict(base, offer=dict(base['offer'], publication=dict(expiration='2020-01-01T00:00:00Z'))),
                dict(base, offer=dict(base['offer'], target_diploma=dict(european='7'))),
                base, base]
        companies, counts = enrich(rows, {siret}, now)
        self.assertEqual(list(companies), [siret])
        self.assertEqual(len(companies[siret]['jobs']), 1)
        self.assertEqual(counts['delegated_skipped'], 1)
        published = json.dumps(companies)
        self.assertNotIn('email', published)
        self.assertNotIn('phone', published)

    def test_echec_second_remplacement_restaure_les_deux_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            targets = [root/'idf/lba', root/'national/lba']
            for target in targets:
                target.mkdir(parents=True)
                (target/'ancien.json').write_text('{"valide":true}')
            pairs = [(preparer_dossier(t, {}, {}, {}), t) for t in targets]
            import os
            real_replace = os.replace
            def fail_once(src, dst):
                if src == pairs[1][0]:
                    raise OSError('Échec de disque simulé')
                return real_replace(src, dst)
            with patch('stage_lba.os.replace', side_effect=fail_once), self.assertRaises(OSError):
                remplacer_dossiers(pairs)
            for target in targets:
                self.assertEqual((target/'ancien.json').read_text(), '{"valide":true}')
                self.assertFalse((target/'meta.json').exists())

    def test_manifest_lba_ne_reference_que_les_fichiers_crees(self):
        with tempfile.TemporaryDirectory() as directory:
            siret = '12345678901234'
            allowed = {siret: {'03/garage', '63/garage'}}
            companies = {siret: dict(recruiter='https://example.test/recruteur')}
            temp = preparer_dossier(Path(directory)/'lba', allowed, companies, {}, True)
            meta = json.loads((temp/'meta.json').read_text())
            self.assertEqual(meta['files'], {'03': ['garage'], '63': ['garage']})
            for dep, sectors in meta['files'].items():
                for sector in sectors:
                    self.assertEqual(json.loads((temp/dep/(sector+'.json')).read_text()), companies)

    def test_lba_deux_catalogues_et_export_incomplet_ne_remplace_rien(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            national, idf = root/'national', root/'idf'
            (national/'.git').mkdir(parents=True)
            (national/'sirene/03').mkdir(parents=True)
            (idf/'data').mkdir(parents=True)
            siret = '12345678901234'
            row = ['Entreprise test', '', 'Adresse test', 46, 3, 1, 0, siret, '']
            raw = json.dumps([row]).encode()
            (national/'sirene/03/garage.json').write_bytes(raw)
            (national/'catalogue.json').write_text(json.dumps(dict(schema=1, complet=True,
                departements={'03': dict(secteurs={'garage': dict(n=1, sha256=hashlib.sha256(raw).hexdigest())})})))
            (idf/'data/index.json').write_text(json.dumps(dict(domaines=[dict(s=[dict(k='garage')])])))
            (idf/'data/garage.json').write_bytes(raw)
            export = root/'export-test.json'
            export.write_text(json.dumps([dict(workplace=dict(siret=siret, email='personne@example.test'),
                identifier=dict(partner_label='recruteurs_lba'), apply=dict(url='https://example.test/recruteur'))]))
            command = [sys.executable, str(ROOT/'source/lba.py'), '--national', '--root', str(national),
                       '--idf-root', str(idf), '--input', str(export), '--write']
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            fr = json.loads((national/'lba/03/garage.json').read_text())
            self.assertEqual(fr, json.loads((idf/'data/lba/garage.json').read_text()))
            self.assertNotIn('email', json.dumps(fr))
            def snapshot():
                return {str(p): p.read_bytes() for base in [national/'lba', idf/'data/lba'] for p in base.rglob('*.json')}
            before = snapshot()
            for damaged in ['[]', '[{"workplace":', '[{"workplace":{"siret":"99999999999999"}}]']:
                export.write_text(damaged)
                result = subprocess.run(command, capture_output=True, text=True, env=env)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(snapshot(), before)


if __name__ == '__main__':
    unittest.main()
