#!/bin/zsh
# Mise à jour trimestrielle : ajoute les établissements créés depuis la dernière fois (stock Sirene le plus
# récent, revérification un par un par l'API), sur une branche, puis ouvre une PR dans carte-stages-donnees.
# Rien n'est publié sans fusion à la main. Lancé par ~/Library/LaunchAgents/fr.azzouz.carte-stages-nouveaux.plist
# (le 3 janvier, avril, juillet et octobre, 7 h), via un lanceur qui exécute la version publiée sur main.
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/bin:/bin
export PYTHONDONTWRITEBYTECODE=1
SITE_DEPOT="${CARTE_STAGES_SITE:-$HOME/Developer/carte-stages}"
DATA_DEPOT="${CARTE_STAGES_DONNEES:-$HOME/Developer/carte-stages-donnees}"
PY="${CARTE_STAGES_PYTHON:-$HOME/Library/Application Support/carte-stages/venv/bin/python}"
ICI="$HOME/Library/Application Support/carte-stages"
JOURNAL_DONNEES="nouveaux-etablissements.json"

VERROU="$ICI/maj-nouveaux.lock"
mkdir -p "$ICI"
mkdir "$VERROU" 2>/dev/null || { echo "Une mise à jour est déjà active : $VERROU"; exit 1; }
trap 'rmdir "$VERROU" 2>/dev/null || true' EXIT
(( $(df -k "$HOME" | awk 'NR==2{print $4}') > 2000000 )) || { echo "Moins de 2 Go libres : arrêt."; exit 1; }
[[ -x "$PY" ]] || { echo "Python avec DuckDB introuvable : $PY"; exit 1; }

for depot nom in "$SITE_DEPOT" carte-stages "$DATA_DEPOT" carte-stages-donnees; do
  [[ "$(git -C "$depot" remote get-url origin)" == *"maths-sciences-lp/$nom"* ]] || { echo "Dépôt inattendu : $depot"; exit 1; }
  git -C "$depot" fetch -q origin main
done

# Stock Sirene le plus récent (fiche data.gouv.fr) et date de départ (dernière mise à jour publiée).
read -r DATE_STOCK URL_ETAB URL_UL <<<"$("$PY" - <<'PYTHON'
import json, urllib.request
d = json.load(urllib.request.urlopen('https://www.data.gouv.fr/api/1/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/', timeout=60))
pq = [r for r in d['resources'] if r['url'].endswith('.parquet')]
etab = next(r for r in pq if 'StockEtablissement -' in r['title'])
ul = next(r for r in pq if 'StockUniteLegale -' in r['title'])
print(etab['last_modified'][:10], etab['url'], ul['url'])
PYTHON
)"
DEPUIS="$(git -C "$DATA_DEPOT" show "origin/main:$JOURNAL_DONNEES" 2>/dev/null | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["date_stock"])' 2>/dev/null || echo 2026-10-01)"
if [[ ! "$DATE_STOCK" > "$DEPUIS" ]]; then echo "Pas de nouveau stock depuis le $DEPUIS : rien à faire."; exit 0; fi
BRANCHE="nouveaux-etablissements-$DATE_STOCK"
if git -C "$DATA_DEPOT" ls-remote --exit-code --heads origin "$BRANCHE" >/dev/null 2>&1; then
  echo "La branche $BRANCHE existe déjà : rien à faire."; exit 0
fi

BASE_TRAVAIL="$(mktemp -d "$ICI/maj-nouveaux-XXXXXXXX")"
SITE_TRAVAIL="$BASE_TRAVAIL/site"; DATA_TRAVAIL="$BASE_TRAVAIL/donnees"; CACHE="$BASE_TRAVAIL/cache"
git -C "$SITE_DEPOT" worktree add -q --detach "$SITE_TRAVAIL" origin/main
git -C "$DATA_DEPOT" worktree add -q -b "$BRANCHE" "$DATA_TRAVAIL" origin/main
OUTIL="$SITE_TRAVAIL/source/stage_nouveaux_codes.py"
"$PY" "$OUTIL" --cache "$CACHE" --phase stock --depuis "$DEPUIS" --url-etablissements "$URL_ETAB" --url-unites "$URL_UL"
"$PY" "$OUTIL" --cache "$CACHE" --phase api
"$PY" "$OUTIL" --cache "$CACHE" --phase ecrire --root "$DATA_TRAVAIL" --rapport "$JOURNAL_DONNEES" --write
"$PY" - "$DATA_TRAVAIL/$JOURNAL_DONNEES" "$DATE_STOCK" "$DEPUIS" <<'PYTHON'
import json, sys
p, stock, depuis = sys.argv[1:]
d = json.load(open(p)); d.update(date_stock=stock, depuis=depuis)
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=1)
PYTHON
AJOUTS="$("$PY" -c 'import json,sys;print(sum(json.load(open(sys.argv[1]))["ajouts"].values()))' "$DATA_TRAVAIL/$JOURNAL_DONNEES")"

git -C "$DATA_TRAVAIL" add -A -- catalogue.json catalogue-leger.json catalogues bilan.json sirene manifestes tailles-fichiers.csv "$JOURNAL_DONNEES"
git -C "$DATA_TRAVAIL" -c user.name=maths-sciences-lp -c user.email=248284752+maths-sciences-lp@users.noreply.github.com \
  commit -q -m "Nouveaux établissements : $AJOUTS ajoutés (créés depuis le $DEPUIS, stock Sirene du $DATE_STOCK)

Mise à jour trimestrielle automatique (source/maj-nouveaux.sh) : établissements
créés depuis la dernière mise à jour, revérifiés un par un par l'API Recherche
d'entreprises, entreprises liquidées écartées. Lignes ajoutées seulement.
Journal : $JOURNAL_DONNEES."
git -C "$DATA_TRAVAIL" push -q -u origin "$BRANCHE"
gh pr create --repo maths-sciences-lp/carte-stages-donnees --base main --head "$BRANCHE" \
  --title "Nouveaux établissements : $AJOUTS ajoutés (stock Sirene du $DATE_STOCK)" \
  --body "Mise à jour trimestrielle préparée par source/maj-nouveaux.sh (carte-stages) : établissements créés depuis le $DEPUIS, revérifiés un par un. À relire puis fusionner à la main. Journal : $JOURNAL_DONNEES."
git -C "$SITE_DEPOT" worktree remove "$SITE_TRAVAIL"
git -C "$DATA_DEPOT" worktree remove --force "$DATA_TRAVAIL"
rm -rf "$BASE_TRAVAIL"
echo "PR ouverte ($AJOUTS établissements)."
