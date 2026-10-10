"""Contrôles hors réseau : catalogue complet, export LBA et conservation sur échec.

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s source -p test_stage_national.py
"""
from collections import Counter
import csv
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

    def test_filiere_bois_menuiserie_bois_et_metal(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        bois, metal = 'menuiserie-bois-agencement', 'menuiserie-metallique-serrurerie'
        self.assertFalse(any('menuiserie-agencement-serrurerie' in s for s in forms.values()))
        for k in ('cap-ebeniste', 'bma-ebeniste', 'cap-charpentier-bois', 'cap-menuisier-fabricant',
                  'bac-pro-technicien-constructeur-bois', 'bac-pro-etude-et-realisation-d-agencement'):
            self.assertEqual([bois in forms[k], metal in forms[k]], [True, False], k)
        for k in ('bac-pro-technicien-menuisier-agenceur',
                  'cap-menuisier-installateur', '2nde-agencement-menuiserie-et-ameublement-mama'):
            self.assertEqual([bois in forms[k], metal in forms[k]], [True, True], k)
        for k in ('cap-metallier', 'bac-pro-ouvrages-du-batiment-metallerie', 'cap-ferronnier-d-art'):
            self.assertEqual([bois in forms[k], metal in forms[k]], [False, True], k)
        from aides import FAMILLES
        self.assertNotIn('bac pro technicien constructeur bois', FAMILLES['Agencement, menuiserie et ameublement (MAMA)'][1])
        def lieu(siret, c, nom):
            return dict(s=siret, n=nom, e='', c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj='5710', du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '43.32A', 'MENUISERIE DUPONT'),
                              lieu('2', '43.32B', 'SERRURERIE MARTIN'),
                              lieu('3', '43.32B', 'MENUISERIE GENERALE LEROY'),   # nom bois : aussi en bois
                              lieu('4', '43.34Z', 'ALUMINIUM CONCEPT AGENCEMENT')])  # nom métal : pas en bois
        dans = {k: sorted(r[7] for r in v) for k, v in groups.items()}
        self.assertEqual(dans[bois], ['1', '3'])
        self.assertEqual(dans[metal], ['2', '3'])

    def test_era_bureau_d_etudes_sans_serrurerie_ni_tapissiers(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        era = forms['bac-pro-etude-et-realisation-d-agencement']
        self.assertEqual(era, ['menuiserie-bois-agencement', 'ebenisterie-meubles-restauration-de-meubles',
                               'architectes', 'design-d-interieur-et-d-objet',
                               'ateliers-de-decors-et-de-musees', 'ateliers-associatifs-du-bois'])
        sieges = 'sieges-reparation-de-meubles'
        for k, s in forms.items():
            if k != 'bac-pro-etude-et-realisation-d-agencement':
                self.assertEqual('ebenisterie-meubles-restauration-de-meubles' in s, sieges in s, k)
        def lieu(siret, c, nom):
            return dict(s=siret, n=nom, e='', c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj='5710', du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '31.09B', 'PRETOLANI AGENCEMENTS'),     # ébéniste : gardé
                              lieu('2', '74.10Z', 'STUDIO AGENCEMENT'),          # design : gardé
                              lieu('3', '43.34Z', 'JHS AGENCEMENT'),             # peinture : non
                              lieu('4', '41.20A', 'LB AGENCEMENT'),              # gros œuvre : non
                              lieu('5', '71.12B', 'PROGEA AGENCEMENT'),          # bureau d'études : non
                              lieu('6', '95.24Z', 'A SIEGE OUVERT'),
                              lieu('7', '31.09A', 'TAPISSIER SEIGNEUR')])
        dans = {k: sorted(r[7] for r in v) for k, v in groups.items()}
        self.assertEqual(dans['menuiserie-bois-agencement'], ['1', '2'])
        self.assertEqual(dans['ebenisterie-meubles-restauration-de-meubles'], ['1'])
        self.assertEqual(dans[sieges], ['6', '7'])

    def test_filiere_graphisme_sans_design_ni_signalisation_routiere(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        design = 'design-d-interieur-et-d-objet'
        for k in ('cap-signaletique-et-decors-graphiques', 'bma-arts-graphiques-option-signaletique',
                  'cap-metiers-de-l-enseigne-et-de-la-signaletique', 'cap-serigraphie-industrielle'):
            self.assertNotIn(design, forms[k], k)
            self.assertIn('publicite-design-graphique', forms[k], k)
        for k, s in forms.items():
            if 'publicite-design-graphique' in s and design not in s:
                self.assertIn(k, ('cap-signaletique-et-decors-graphiques', 'bma-arts-graphiques-option-signaletique',
                                  'cap-metiers-de-l-enseigne-et-de-la-signaletique', 'cap-serigraphie-industrielle'))
        def lieu(siret, c, nom):
            return dict(s=siret, n=nom, e='', c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj='5710', du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '73.11Z', 'ENSEIGNES DUPONT'),
                              lieu('2', '42.11Z', 'MSR MARQUAGE SIGNALISATION ROUTIERE'),
                              lieu('3', '42.11Z', 'LDV SIGNALISATION'),
                              lieu('4', '18.13Z', 'SOUARD MARQUAGE VEHICULES')])
        self.assertEqual(sorted(r[7] for r in groups['enseignes-signaletique-marquage']), ['1', '4'])

    def test_services_techniques_hopitaux_et_bailleurs_sociaux(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        imtb = forms['cap-interventions-en-maintenance-technique-des-batiments']
        self.assertNotIn('agences-immobilieres-gestion-de-logements', imtb)
        self.assertIn('hopitaux-services-techniques', imtb)
        self.assertIn('bailleurs-sociaux', imtb)
        self.assertNotIn('hopitaux-services-techniques', forms['bac-pro-accompagnement-soins-et-services-a-la-personne'])
        def lieu(siret, c, nom, e='', nj='5710'):
            return dict(s=siret, n=nom, e=e, c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='53', nj=nj, du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '86.10Z', 'ASSISTANCE PUBLIQUE HOPITAUX DE PARIS', 'HOPITAL TENON', '7364'),
                              lieu('2', '86.10Z', 'GROUPE HOSPITALIER UNIVERSITAIRE PARIS', 'CMP LA CHAPELLE', '7364'),
                              lieu('3', '86.10Z', 'CLINIQUE DES PLATANES'),
                              lieu('4', '86.90B', 'LABORATOIRE CERBALLIANCE'),
                              lieu('5', '68.20A', 'OPH EST ENSEMBLE HABITAT', nj='4140'),
                              lieu('6', '68.20A', 'SCI PARIS LIBERTE', nj='6540'),
                              lieu('7', '68.32A', 'CABINET DE SYNDIC'),
                              lieu('8', '68.20A', 'SAEM NOISY-LE-SEC HABITAT', nj='5515')])
        dans = {k: sorted(r[7] for r in v) for k, v in groups.items()}
        self.assertEqual(dans['hopitaux-services-techniques'], ['1', '3'])
        self.assertEqual(dans['hopitaux-cliniques-laboratoires'], ['1', '2', '3', '4'])
        self.assertEqual(dans['bailleurs-sociaux'], ['5', '8'])
        self.assertEqual(dans['agences-immobilieres-gestion-de-logements'], ['5', '6', '7', '8'])

    def test_nouveaux_codes_et_seuils(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        self.assertIn('promotion-immobiliere', forms['bac-pro-technicien-d-etudes-du-batiment-option-a-etudes-et-e'])
        self.assertNotIn('promotion-immobiliere', forms['bac-pro-geometre'])
        def lieu(siret, c, nom, t='11', nj='5710'):
            return dict(s=siret, n=nom, e='', c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t=t, nj=nj, du='O', de='O', r=False)
        groups, excl = preparer([lieu('1', '41.10A', 'BOUYGUES IMMOBILIER', '41'),
                                 lieu('2', '41.10A', 'SCI DU PATIO', '11', '6540'),
                                 lieu('3', '41.10C', 'IDEEA DEVELOPPEMENT', '01'),
                                 lieu('4', '26.40Z', 'TRINNOV AUDIO', '21'),
                                 lieu('5', '26.40Z', 'LIPSTECH', '01'),
                                 lieu('6', '95.21Z', 'MONDIAL TELE', '01'),
                                 lieu('7', '16.22Z', 'PARQUETS PEDUSSAUT', '01')])
        dans = {k: sorted(r[7] for r in v) for k, v in groups.items()}
        self.assertEqual(dans['promotion-immobiliere'], ['1'])
        self.assertEqual(dans['electronique-materiel-electrique'], ['4'])
        self.assertEqual(dans['reparation-d-ordinateurs-et-de-telephones'], ['6'])
        self.assertEqual(dans['menuiserie-bois-agencement'], ['7'])
        self.assertEqual(excl['sous_le_seuil'], 3)

    def test_lot_batiment_travaux_publics(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        ce = forms['cap-conducteur-d-engins-de-travaux-publics-et-carrieres']
        self.assertIn('carrieres', ce)
        self.assertIn('demolition', ce)
        self.assertNotIn('demolition', forms['bac-pro-geometre'])
        def lieu(siret, c, nom, t='11'):
            return dict(s=siret, n=nom, e='', c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t=t, nj='5710', du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '08.12Z', 'CEMEX GRANULATS', '32'), lieu('2', '42.12Z', 'ETF', '42'),
                              lieu('3', '43.11Z', 'PREMYS', '41'), lieu('4', '43.11Z', 'AURUS', '01')])
        dans = {k: sorted(r[7] for r in v) for k, v in groups.items()}
        self.assertEqual(dans['carrieres'], ['1'])
        self.assertEqual(dans['travaux-publics-routes-reseaux'], ['2'])
        self.assertEqual(dans['demolition'], ['3'])

    def test_lycees_et_colleges_publics(self):
        from stage_etablissements_scolaires import lignes
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        self.assertIn('lycees-publics-maintenance', forms['cap-interventions-en-maintenance-technique-des-batiments'])
        self.assertNotIn('colleges-publics-maintenance', forms['bac-pro-geometre'])
        def e(uai, nom, t, siret, la=48.87):
            return dict(identifiant_de_l_etablissement=uai, nom_etablissement=nom, type_etablissement=t,
                        adresse_1='55 avenue Raspail', code_postal='93170', nom_commune='Bagnolet',
                        latitude=la, longitude=2.43, siren_siret=siret, code_departement='093')
        f, ecartes = lignes([e('1', 'Lycée polyvalent Eugène Henaff', 'Lycée', '19932119100017'),
                             e('2', "Section d'enseignement professionnel du Lycée Eugène Henaff", 'Lycée', '19932119100025'),
                             e('3', 'Collège Travail Langevin', 'Collège', '19930001000011', 48.86),
                             e('4', 'Collège sans SIRET', 'Collège', None, 48.85)], {'93'})
        self.assertEqual([r[0] for r in f[('93', 'lycees-publics-maintenance')]], ['Lycée polyvalent Eugène Henaff'])
        self.assertEqual([r[0] for r in f[('93', 'colleges-publics-maintenance')]], ['Collège Travail Langevin'])
        self.assertEqual(ecartes, {'section_interne': 1, 'sans_siret_ou_position': 1})

    def test_noms_filtres_design_architectes_et_mentions(self):
        def lieu(siret, c, nom):
            return dict(s=siret, n=nom, e='', c=c, q=c, ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj='5710', du='O', de='O', r=False)
        groups, _ = preparer([lieu('1', '74.10Z', 'WOM DESIGN'), lieu('2', '74.10Z', 'ELITE RENOV'),
                              lieu('3', '71.11Z', 'ATELIER PAF ARCHITECTES'), lieu('4', '71.11Z', 'HOLDING POLO'),
                              lieu('5', '71.11Z', 'SEML RESILIENCE ((SUPPRESSION))')])
        dans = {k: sorted(r[7] for r in v) for k, v in groups.items()}
        self.assertEqual(dans['design-d-interieur-et-d-objet'], ['1'])
        self.assertEqual(dans['architectes'], ['3', '5'])
        self.assertEqual([r[0] for r in groups['architectes'] if r[7] == '5'], ['SEML RESILIENCE'])

    def test_routes_de_l_etat(self):
        forms = {f['k']: f['s'] for f in catalogue_formations()['formations']}
        etudes, entretien = 'routes-de-l-etat-etudes-et-districts', 'routes-de-l-etat-centres-d-entretien'
        self.assertEqual([etudes in forms['bac-pro-geometre'], entretien in forms['bac-pro-geometre']], [True, False])
        self.assertTrue({etudes, entretien} <= set(forms['bac-pro-travaux-publics']))
        def lieu(siret, nom, ens):
            return dict(s=siret, n=nom, e=ens, c='84.13Z', q='84.13Z', ad='1 rue X 01000 Y', la=46.0, lo=5.0,
                        t='11', nj='7172', du='O', de='O', r=False)
        groups, _ = preparer([lieu('13000171200491', 'DIRECTION INTERDEPARTEMENTALE DES ROUTES ATLANTIQUE', 'SIR DE BORDEAUX'),
                              lieu('13000171200500', 'DIRECTION INTERDEPARTEMENTALE DES ROUTES ATLANTIQUE', 'CEI DE SAINTES'),
                              lieu('13000171200600', 'DIRECTION INTERDEPARTEMENTALE DES ROUTES ATLANTIQUE', 'CIGT DE BORDEAUX'),
                              lieu('13002932500334', 'DRIEAT', 'AGER-NORD/CEI ROSNY SOUS BOIS'),
                              lieu('13002932500037', 'DRIEAT', 'DRIEAT/UD93'),
                              lieu('13000000000001', 'FRANCE TRAVAIL', 'AGENCE DE LAON')])
        dans = {r[7]: k for k, v in groups.items() for r in v}
        self.assertEqual(dans, {'13000171200491': etudes, '13000171200500': entretien, '13000171200600': 'mairies-administrations',
                                '13002932500334': entretien, '13002932500037': 'mairies-administrations',
                                '13000000000001': 'mairies-administrations'})

    def test_bodacc_seule_la_liquidation_retire(self):
        from stage_bodacc import liquidees
        def j(nature, date):
            return json.dumps(dict(nature=nature, date=date), ensure_ascii=False)
        lignes = [('1', '111111111', '2026-01-10', 'annonce', j("Jugement d'ouverture de liquidation judiciaire", '2026-01-05')),
                  ('2', '222222222', '2025-03-01', 'annonce', j("Jugement d'ouverture d'une procédure de redressement judiciaire", '2025-02-20')),
                  ('3', '333333333', '2025-03-01', 'annonce', j("Jugement d'ouverture d'une procédure de redressement judiciaire", '2025-02-20')),
                  ('4', '333333333', '2026-02-01', 'annonce', j('Jugement de conversion en liquidation judiciaire', '2026-01-25')),
                  ('5', '444444444', '2025-05-01', 'annonce', j("Jugement d'ouverture de liquidation judiciaire", '2025-04-20')),
                  ('6', '444444444', '2025-09-01', 'annonce', j("Arrêt de la cour d'appel infirmant une décision soumise à publicité", '2025-08-20')),
                  ('7', '555555555', '2026-01-10', 'rectificatif', j("Jugement d'ouverture de liquidation judiciaire", '2026-01-05'))]
        with tempfile.TemporaryDirectory() as t:
            path = Path(t)/'c.csv'
            with path.open('w', newline='', encoding='utf-8') as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(['id', 'registre', 'dateparution', 'typeavis', 'jugement'])
                for i, siren, d, ty, ju in lignes:
                    w.writerow([i, siren + ',' + siren[:3] + ' ' + siren[3:6] + ' ' + siren[6:], d, ty, ju])
            self.assertEqual(sorted(liquidees(path)), ['111111111', '333333333'])

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
