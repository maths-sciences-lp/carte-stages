"""Contrôle reproductible des ajouts France, sans réseau ni écriture par défaut.

python3 source/audit_formations_france.py
python3 source/audit_formations_france.py --rapport /tmp/formations-france.md

Le dossier de preuves JSON conserve uniquement des informations sur les diplômes
et des agrégats LBA. La base Git est fixée avant les ajouts pour rester vérifiable
après une éventuelle fusion. Aucune recherche approximative n'ajoute de diplôme.
"""
import argparse
import collections
import json
from pathlib import Path
import re
import subprocess
import unicodedata

from domaines import DOMAINES, FILTRES, MOTS_CLES, SOURCES_MOTS_CLES

ROOT = Path(__file__).resolve().parents[1]


def normaliser(titre):
    titre = titre.casefold().replace('œ', 'oe').replace('æ', 'ae')
    titre = re.sub(r'\bcap\s+agricole\b', 'capa', titre)
    titre = ''.join(c for c in unicodedata.normalize('NFKD', titre)
                    if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', titre).strip()


def lire_git(base, fichier):
    return subprocess.check_output(['git', 'show', base + ':' + fichier],
                                   cwd=ROOT, text=True)


def verifier():
    meta = json.loads((ROOT / 'source/formation_secteurs_france.json').read_text())
    base = meta['base_git']
    anciens = json.loads(lire_git(base, 'source/formation_secteurs.json'))
    table = json.loads((ROOT / 'source/formation_secteurs.json').read_text())
    erreurs = []

    def check(condition, message):
        if not condition:
            erreurs.append(message)

    check(all(table.get(n) == s for n, s in anciens.items()),
          'Une formation ou association préexistante a changé.')
    check(len({normaliser(n) for n in table}) == len(table),
          'Doublon après normalisation des intitulés.')
    # Le code provient de la révision Git de référence de ce même dépôt.
    espace = {}
    exec(compile(lire_git(base, 'source/domaines.py'), 'domaines_reference', 'exec'), espace)
    vieux = espace['DOMAINES']
    check(all(DOMAINES.get(d, {}).get(s) == cs
              for d, ss in vieux.items() for s, cs in ss.items()),
          'Un secteur ou une liste NAF préexistante a changé.')
    check(MOTS_CLES == espace['MOTS_CLES'] and SOURCES_MOTS_CLES == espace['SOURCES_MOTS_CLES'],
          'Les règles historiques par mots-clés ont changé.')
    check(all(FILTRES.get(s) == rx for s, rx in espace['FILTRES'].items()),
          'Un filtre historique a changé.')
    titres, offres, fichiers = {}, collections.Counter(), []
    for p in sorted((ROOT / 'apres-3e/data').glob('*.json')):
        contenu = json.loads(p.read_text())
        if 'formations' not in contenu:
            continue  # bilan.json n'est pas une académie
        fichiers.append(p.name)
        for f in contenu['formations']:
            if f['n'].casefold().startswith(('cap', 'bac pro')):
                titres.setdefault(normaliser(f['n']), f['n'])
                offres[normaliser(f['n'])] += len(f['e'])
    reference = {normaliser(n) for n in anciens}
    manquants = set(titres) - reference
    ajouts = set(table) - set(anciens)
    check({normaliser(n) for n in ajouts} == manquants,
          'Les ajouts ne correspondent pas exactement aux diplômes absents.')
    preuves = {f['intitule']: f for f in meta['formations']}
    check(set(preuves) == ajouts and len(preuves) == len(meta['formations']),
          'Le dossier de preuves ne couvre pas exactement les ajouts.')
    secteurs = {s: cs for ss in DOMAINES.values() for s, cs in ss.items()}
    vieux_codes = {c for ss in vieux.values() for cs in ss.values() for c in cs}
    nouveaux_codes = {c for cs in secteurs.values() for c in cs} - vieux_codes
    check(nouveaux_codes == set(meta['nouveaux_codes_naf']), 'Inventaire des nouveaux NAF incomplet.')
    secteurs_ajoutes = {d: {s: cs for s, cs in ss.items() if s not in vieux.get(d, {})}
                       for d, ss in DOMAINES.items()}
    secteurs_ajoutes = {d: ss for d, ss in secteurs_ajoutes.items() if ss}
    check(secteurs_ajoutes == meta['nouveaux_secteurs'], 'Inventaire des nouveaux secteurs différent.')
    slugs = [re.sub(r'[^a-z0-9]+', '-', ''.join(c for c in unicodedata.normalize('NFD', s.lower())
                                             if unicodedata.category(c) != 'Mn')).strip('-')[:60]
             for s in secteurs]
    check(len(slugs) == len(set(slugs)), 'Collision des noms de fichiers de secteurs.')
    for n, f in preuves.items():
        check(f['marquage'] == 'ajout France' and f['secteurs'] == table[n], 'Marquage/secteurs : ' + n)
        check(bool(f['justification_onisep']) and f['onisep']['url'].startswith('https://www.onisep.fr/'),
              'Source Onisep manquante : ' + n)
        check(all(s in secteurs for s in f['secteurs']), 'Secteur inconnu : ' + n)
        check([a['secteur'] for a in f['associations']] == f['secteurs'], 'Preuves des associations : ' + n)
        c, signal = f['certification_lba'], f['signal_lba']
        check((c is None and signal is None and f['limites']) or (c is not None and signal is not None),
              'RNCP/signal absent sans explication : ' + n)
        if c and signal:
            check(bool(re.fullmatch(r'RNCP\d{3,5}', c['rncp'])) and
                  'rncp=' + c['rncp'] in signal['source'], 'RNCP de la recherche : ' + n)
            check('target_diploma_level=' + ('3' if n.startswith('CAP') else '4') in signal['source'],
                  'Niveau de la recherche LBA : ' + n)
            check(bool(c['rome']) and all(re.fullmatch(r'[A-Z]\d{4}', r['code']) for r in c['rome']),
                  'Codes ROME absents ou invalides : ' + n)
        for a in f['associations']:
            check(a['codes_naf'] == secteurs[a['secteur']], 'NAF de l’association : ' + n)
            if signal:
                for genre in ('jobs', 'recruiters'):
                    check(a['signal_lba'][genre] == sum(signal[genre]['par_naf'].get(code, 0)
                                                       for code in a['codes_naf']),
                          'Agrégat LBA incohérent : ' + n)
                    check(sum(signal[genre]['par_naf'].values()) + signal[genre]['exclus'] == signal[genre]['retournes'],
                          'Total LBA incohérent : ' + n)
    # Préserver les fichiers réellement servis, y compris LBA, les pages et les licences.
    changements = subprocess.check_output(['git', 'diff', '--name-only', base, '--',
                                          '.', ':!source/'], cwd=ROOT, text=True).splitlines()
    check(not changements, 'Fichiers hors source/ modifiés : ' + ', '.join(changements))
    stats = dict(academies=len(fichiers), formations=len(titres), anciens=len(anciens),
                 ajouts=len(ajouts), cap=sum(n.startswith('CAP') for n in ajouts),
                 capa=sum(n.startswith('CAPa ') for n in ajouts),
                 bac=sum(n.startswith('bac pro ') for n in ajouts),
                 offres=sum(offres[n] for n in manquants), naf=len(nouveaux_codes),
                 secteurs=sum(len(s) for s in secteurs_ajoutes.values()))
    return meta, stats, erreurs


def rapport(meta, stats):
    lignes = ['# Ajouts France — formations et entreprises', '',
              f"Contrôle du {meta['date_controle'][:10]} ; référence Git `{meta['base_git']}`.", '',
              f"{stats['formations']} intitulés CAP/bac pro dans {stats['academies']} académies ; "
              f"{stats['ajouts']} absents de la table : {stats['cap']} CAP (dont {stats['capa']} CAPa), "
              f"{stats['bac']} bacs pro. Ils représentent {stats['offres']} occurrences formation–établissement "
              "dans ces fichiers (pas des places ni des offres d'emploi).", '',
              f"Les {stats['anciens']} entrées historiques et leurs associations sont conservées. "
              f"{stats['secteurs']} secteurs et {stats['naf']} codes NAF sont ajoutés ; "
              "aucune ancienne liste NAF n'est modifiée.", '', '## Méthode et portée', '', meta['methode'], '',
              'Sources : fiches Onisep déjà téléchargées pour la mission Après le lycée (dates et SHA-256 '
              'dans le JSON), catalogue de certifications et recherche LBA consultés le 7 octobre 2026, '
              '[NAF rév. 2 de l’Insee](https://www.insee.fr/fr/information/2120875). '
              'La NAF 2025 n’est pas utilisée pour cette collecte en NAF rév. 2.', '',
              'Les nombres LBA ci-dessous sont des résultats de recherche, pas des recrutements réalisés. '
              'Les offres et les recruteurs potentiels sont séparés. La réponse est partielle '
              '(souvent 150 recruteurs) et les codes ROME peuvent englober plusieurs options. '
              'On ne somme pas les lignes entre diplômes. Les offres déléguées à des CFA et celles '
              'explicitement inactives sont exclues des agrégats ; le filtre de niveau accepte aussi '
              'les niveaux non renseignés. Le filtre de nom du nouveau secteur des fleurs n’est pas '
              'appliqué au signal NAF : celui-ci peut donc être plus large.', '',
              'Aucune coordonnée de candidat, de contact ou d’entreprise n’est enregistrée dans ce dossier. '
              'La clé API est lue uniquement en mémoire. Aucun téléchargement Sirene n’est lancé par les scripts d’audit.', '',
              'Cette PR prépare les sources. Les JSON et pages actuellement servis restent inchangés. '
              'Régénérer le catalogue de stages avec ces sources ajoutera ces formations et secteurs : '
              'la future mission nationale devra conserver le catalogue Île-de-France publié.', '',
              '## Points à relire en priorité', '',
              '- RNCP non rapproché : CAP agent de développement des activités locales option tourisme (Guyane), '
              'et certificat polynésien petite et moyenne hôtellerie. Ce dernier est rattaché par Onisep à Mana, en Guyane.',
              '- Trois bacs pro de conduite des entreprises maritimes : code ROME N3202 fluvial renvoyé par '
              'la certification ; les secteurs maritimes retenus suivent Onisep. Aucun lien fluvial déduit de ce seul code.',
              '- Réparation/accordage des instruments : le code 95.29Z reste dans le secteur historique de pressing. '
              'Couverture partielle assumée ; aucune entreprise déplacée et aucun lien trompeur ajouté au pressing.',
              '- NAF larges : équitation, élevage, animaleries de laboratoire, armurerie, tourisme, photonique, '
              'parcs et déchets dangereux. Vérifier la spécialité réelle avant de proposer un stage.',
              '- Artisans individuels toujours exclus de la future collecte : limite forte pour la maréchalerie '
              'et les métiers d’art. Le filtre nouveau 32.99Z sur les noms de fabricants de fleurs demande une relecture.', '',
              '## Nouveaux codes NAF', '', '| Code | Libellé Insee | Secteur |', '|---|---|---|']
    for code, f in sorted(meta['nouveaux_codes_naf'].items()):
        lignes.append(f"| [{code}]({f['source']}) | {f['libelle_insee']} | {f['secteur']} |")
    lignes += ['', '## Justifications par formation', '']
    for i, f in enumerate(meta['formations'], 1):
        lignes += [f"### {i}. {f['intitule']} — ajout France", '',
                   '**Types d’entreprises :** ' + ' ; '.join(f['secteurs']) + '.', '',
                   '**Lecture Onisep :** ' + f['justification_onisep'], '',
                   f"[Fiche diplôme Onisep]({f['onisep']['url']})."]
        c = f['certification_lba']
        if c:
            lignes += [f"[{c['rncp']}]({c['url_rncp']}) ; CFD `{c['cfd']}` ; "
                       f"[certification via LBA]({c['source']}). ROME : " +
                       ' ; '.join(r['code'] + ' — ' + r['intitule'] for r in c['rome']) + '.', '']
            s = f['signal_lba']
            lignes += [f"[Recherche LBA]({s['source']}) : {s['jobs']['retournes']} offres retournées "
                       f"({s['jobs']['exclus']} exclues), {s['recruiters']['retournes']} recruteurs potentiels. "
                       'Répartition des résultats retenus par secteur (offres / recruteurs) :', '']
            lignes += [f"- {a['secteur']} : {a['signal_lba']['jobs']} / {a['signal_lba']['recruiters']}."
                       for a in f['associations']]
        else:
            lignes += ['', 'RNCP, ROME et signal LBA : **non rapprochés**, sans estimation.']
        if f['limites']:
            lignes += ['', '**Limites / cas incertains :**'] + ['- ' + n for n in f['limites']]
        lignes.append('')
    return '\n'.join(lignes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rapport', type=Path)
    args = parser.parse_args()
    meta, stats, erreurs = verifier()
    print(f"{stats['formations']} formations nationales ; {stats['ajouts']} ajouts : "
          f"{stats['cap']} CAP dont {stats['capa']} CAPa, {stats['bac']} bacs pro.")
    print(f"{stats['offres']} occurrences formation–établissement concernées.")
    print(f"{stats['anciens']} formations historiques inchangées ; "
          f"{stats['secteurs']} secteurs et {stats['naf']} codes NAF ajoutés.")
    for erreur in erreurs:
        print('ERREUR : ' + erreur)
    print('Contrôle des ajouts France : ' + ('échec' if erreurs else 'réussi'))
    if erreurs:
        raise SystemExit(1)
    if args.rapport:
        args.rapport.write_text(rapport(meta, stats) + '\n')


if __name__ == '__main__':
    main()
