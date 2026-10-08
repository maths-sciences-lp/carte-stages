#!/bin/zsh
# PROPOSITION À RELIRE : ne remplace pas la tâche launchd installée.
# Sans argument : prépare deux copies locales, sans publication.
# Après validation et installation seulement : --publier pour la tâche mensuelle.
# Un échec conserve les fichiers servis. Les copies préparées restent inspectables.
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin
export PYTHONDONTWRITEBYTECODE=1
SITE_DEPOT="${CARTE_STAGES_SITE:-$HOME/Developer/carte-stages}"
DATA_DEPOT="${CARTE_STAGES_DONNEES:-$HOME/Developer/carte-stages-donnees-france}"
MODE="${1:---preparer}"
[[ "$MODE" == --preparer || "$MODE" == --publier ]] || { echo "Usage : $0 [--preparer|--publier]"; exit 2; }

ECHEC="La mise à jour n’a pas été publiée. Les fichiers précédents restent en ligne."
BASE_TRAVAIL=""
trap 'echo "$ECHEC"; [[ -z "$BASE_TRAVAIL" ]] || echo "Copies conservées : $BASE_TRAVAIL"' ZERR

# Verrou de la tâche mensuelle, distinct du collecteur Sirene.
VERROU="$HOME/Library/Application Support/carte-stages/maj-lba-national.lock"
mkdir -p "${VERROU:h}"
if ! mkdir "$VERROU" 2>/dev/null; then
  echo "Une mise à jour est déjà active, ou son verrou attend une vérification : $VERROU"
  exit 1
fi
trap 'rmdir "$VERROU" 2>/dev/null || true' EXIT

verifier_depot() {
  local copie="$1" nom="$2" distant
  distant="$(git -C "$copie" remote get-url origin)"
  [[ "$distant" == "https://github.com/maths-sciences-lp/$nom.git" ||
     "$distant" == "https://github.com/maths-sciences-lp/$nom" ||
     "$distant" == "git@github.com:maths-sciences-lp/$nom.git" ]] || {
    echo "Dépôt inattendu : $copie"; return 1
  }
  git -C "$copie" fetch -q origin main
}
verifier_depot "$SITE_DEPOT" carte-stages
verifier_depot "$DATA_DEPOT" carte-stages-donnees
BASE_SITE="$(git -C "$SITE_DEPOT" rev-parse origin/main)"
BASE_DATA="$(git -C "$DATA_DEPOT" rev-parse origin/main)"
BASE_TRAVAIL="$(mktemp -d "$HOME/Library/Application Support/carte-stages/maj-lba-XXXXXXXX")"
SITE_TRAVAIL="$BASE_TRAVAIL/site"
DATA_TRAVAIL="$BASE_TRAVAIL/donnees"
git -C "$SITE_DEPOT" worktree add -q --detach "$SITE_TRAVAIL" "$BASE_SITE"
git -C "$DATA_DEPOT" worktree add -q --detach "$DATA_TRAVAIL" "$BASE_DATA"

# L'export brut et la clé ne sont jamais écrits. Le programme ne remplace les
# dossiers de ces copies qu'après lecture complète et validation de l'export.
python3 "$SITE_TRAVAIL/source/lba.py" --national --root "$DATA_TRAVAIL" --idf-root "$SITE_TRAVAIL" --write
python3 - "$SITE_TRAVAIL" "$DATA_TRAVAIL" <<'PY'
import json,re,sys
from datetime import datetime
from pathlib import Path
site,data=map(Path,sys.argv[1:])
for root in [site/'data/lba',data/'lba']:
    for path in root.rglob('*.json'):
        json.loads(path.read_text())
if json.loads((site/'data/lba/meta.json').read_text())['updated_at'] != json.loads((data/'lba/meta.json').read_text())['updated_at']:
    raise ValueError('Dates des deux exports différentes')
version=datetime.now().strftime('%Y-%m-%d-%H%M%S')+'-lba'
for path in [site/'index.html',site/'source/public3_template.html']:
    new,n=re.subn(r"const DV='[^']*'", "const DV='"+version+"'",path.read_text())
    if n != 1: raise ValueError('Version DV absente ou ambiguë')
    path.write_text(new)
PY

committer() {
  local copie="$1"; shift
  git -C "$copie" diff --check
  git -C "$copie" add -A -- "$@"
  if ! git -C "$copie" diff --cached --quiet; then
    git -C "$copie" -c user.name=maths-sciences-lp \
      -c user.email=248284752+maths-sciences-lp@users.noreply.github.com \
      commit -q -m "La bonne alternance : mise à jour mensuelle ($(date +%d/%m/%Y))"
  fi
}
committer "$DATA_TRAVAIL" lba
committer "$SITE_TRAVAIL" data/lba index.html source/public3_template.html
echo "Deux versions préparées et vérifiées : $BASE_TRAVAIL"
if [[ "$MODE" != --publier ]]; then
  echo "Rien publié. Ces copies Git conservent les commits pour relecture."
  exit 0
fi

# Pas de push forcé, pas de réécriture d'historique. Les deux pushes ne sont
# pas atomiques : si le second échoue, l'IDF garde ses anciennes données valides.
# Vérifier les deux bases avant le premier push limite ce risque.
git -C "$SITE_TRAVAIL" fetch -q origin main
git -C "$DATA_TRAVAIL" fetch -q origin main
[[ "$(git -C "$SITE_TRAVAIL" rev-parse origin/main)" == "$BASE_SITE" &&
   "$(git -C "$DATA_TRAVAIL" rev-parse origin/main)" == "$BASE_DATA" ]] || {
  echo "Main a changé pendant la préparation : publication annulée, copies conservées."
  exit 1
}
git -C "$DATA_TRAVAIL" push -q origin HEAD:main
ECHEC="Les données nationales ont été poussées ; l’Île-de-France garde sa dernière version. La copie site est conservée pour terminer la publication."
git -C "$SITE_TRAVAIL" push -q origin HEAD:main
echo "Deux mises à jour poussées. Le déploiement GitHub Pages reste à vérifier."
git -C "$SITE_DEPOT" worktree remove "$SITE_TRAVAIL"
git -C "$DATA_DEPOT" worktree remove "$DATA_TRAVAIL"
rmdir "$BASE_TRAVAIL"
