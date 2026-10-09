#!/bin/zsh
# Retrait mensuel des entreprises liquidées (BODACC) : prépare une PR dans carte-stages-donnees,
# sans rien publier. La PR est fusionnée à la main, après relecture.
# Lancé par ~/Library/LaunchAgents/fr.azzouz.carte-stages-bodacc.plist (le 2 du mois, 7 h),
# via un lanceur qui exécute la version de ce fichier publiée sur main.
# Un échec ne change rien en ligne ; les copies de travail restent inspectables.
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin
export PYTHONDONTWRITEBYTECODE=1
SITE_DEPOT="${CARTE_STAGES_SITE:-$HOME/Developer/carte-stages}"
DATA_DEPOT="${CARTE_STAGES_DONNEES:-$HOME/Developer/carte-stages-donnees}"
ICI="$HOME/Library/Application Support/carte-stages"
MOIS="$(date +%Y-%m)"
BRANCHE="liquidations-$MOIS"

VERROU="$ICI/maj-bodacc.lock"
mkdir -p "$ICI"
mkdir "$VERROU" 2>/dev/null || { echo "Une mise à jour est déjà active : $VERROU"; exit 1; }
trap 'rmdir "$VERROU" 2>/dev/null || true' EXIT

# Arrêt si moins de 2 Go libres (l'export BODACC pèse environ 400 Mo).
(( $(df -k "$HOME" | awk 'NR==2{print $4}') > 2000000 )) || { echo "Moins de 2 Go libres : arrêt."; exit 1; }

for depot nom in "$SITE_DEPOT" carte-stages "$DATA_DEPOT" carte-stages-donnees; do
  [[ "$(git -C "$depot" remote get-url origin)" == *"maths-sciences-lp/$nom"* ]] || { echo "Dépôt inattendu : $depot"; exit 1; }
  git -C "$depot" fetch -q origin main
done
if git -C "$DATA_DEPOT" ls-remote --exit-code --heads origin "$BRANCHE" >/dev/null 2>&1; then
  echo "La branche $BRANCHE existe déjà : rien à faire ce mois-ci."; exit 0
fi

BASE_TRAVAIL="$(mktemp -d "$ICI/maj-bodacc-XXXXXXXX")"
SITE_TRAVAIL="$BASE_TRAVAIL/site"
DATA_TRAVAIL="$BASE_TRAVAIL/donnees"
git -C "$SITE_DEPOT" worktree add -q --detach "$SITE_TRAVAIL" origin/main
git -C "$DATA_DEPOT" worktree add -q -b "$BRANCHE" "$DATA_TRAVAIL" origin/main

python3 "$SITE_TRAVAIL/source/stage_bodacc.py" --root "$DATA_TRAVAIL" --write | tee "$BASE_TRAVAIL/bilan.json"
RETIRES="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["etablissements_retires"])' "$BASE_TRAVAIL/bilan.json")"

git -C "$DATA_TRAVAIL" add -A -- catalogue.json catalogue-leger.json catalogues bilan.json sirene lba tailles-fichiers.csv liquidations-bodacc.json manifestes
if [[ "$RETIRES" == 0 ]] || git -C "$DATA_TRAVAIL" diff --cached --quiet; then
  echo "Aucune nouvelle liquidation ce mois-ci : pas de PR."
  git -C "$SITE_DEPOT" worktree remove "$SITE_TRAVAIL"
  git -C "$DATA_DEPOT" worktree remove --force "$DATA_TRAVAIL"
  git -C "$DATA_DEPOT" branch -D "$BRANCHE" >/dev/null
  rmdir "$BASE_TRAVAIL" 2>/dev/null || rm -rf "$BASE_TRAVAIL"
  exit 0
fi
git -C "$DATA_TRAVAIL" -c user.name=maths-sciences-lp -c user.email=248284752+maths-sciences-lp@users.noreply.github.com \
  commit -q -m "Liquidations judiciaires (BODACC) : $RETIRES établissements retirés ($MOIS)

Retrait mensuel automatique (source/maj-bodacc.sh) : dernière décision BODACC
par entreprise, liquidation seulement. Journal : liquidations-bodacc.json."
git -C "$DATA_TRAVAIL" push -q -u origin "$BRANCHE"
gh pr create --repo maths-sciences-lp/carte-stages-donnees --base main --head "$BRANCHE" \
  --title "Liquidations judiciaires (BODACC) : $RETIRES établissements retirés ($MOIS)" \
  --body "Retrait mensuel automatique préparé par source/maj-bodacc.sh (carte-stages). À relire puis fusionner à la main. Journal : liquidations-bodacc.json.

Bilan : $(tr '\n' ' ' < "$BASE_TRAVAIL/bilan.json" | cut -c1-600)"
git -C "$SITE_DEPOT" worktree remove "$SITE_TRAVAIL"
git -C "$DATA_DEPOT" worktree remove --force "$DATA_TRAVAIL"
rm -rf "$BASE_TRAVAIL"
echo "PR ouverte ($RETIRES établissements)."
