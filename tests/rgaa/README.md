# Vérifications d’accessibilité locales

Serveur : `python3 -m http.server 8768 --bind 127.0.0.1` à la racine de la copie.
Installer Playwright et axe-core dans un dossier de test externe, jamais dans les pages.

- `PLAYWRIGHT_MODULE=/chemin/node_modules/playwright AXE_PATH=/chemin/node_modules/axe-core/axe.min.js OUTPUT=/tmp/rgaa-apres node tests/rgaa/audit.cjs`
- `PLAYWRIGHT_MODULE=/chemin/node_modules/playwright node tests/rgaa/clavier.cjs`
- `PLAYWRIGHT_MODULE=/chemin/node_modules/playwright node tests/rgaa/complements.cjs`
- `python3 source/verif_idf.py --accessibilite --sources-idf <cache> --sources-apres3e <cache> --sources-formation <cache> --rapport /tmp/verif-idf-rgaa`

`BASE_URL` permet de changer le serveur. Sans `--accessibilite`, le contrôle Île-de-France conserve sa comparaison stricte du texte affiché. Avec cette option, seuls les ajouts de libellés, de navigation, de statut et d’indicateurs de nouvel onglet explicitement identifiés sont exclus. Les textes bruts et les champs sont conservés dans le rapport ; aucun filtre sur les données métier.

Les tests automatiques ne remplacent pas la validation de restitution par lecteurs d’écran. La déclaration et le rapport signalent explicitement cette limite.
