#!/usr/bin/env bash
# Respaldo permanente del conteo vehicular 1PIXEL.
# Vuelca todos los snapshots diarios (KV del Worker) a JSON versionado en este repo.
# Correr periódicamente (semanal) para que el archivo crezca con cada día nuevo.
#
#   ./refresh-archive.sh           # exporta y deja los JSON listos para commit
#   ./refresh-archive.sh --push    # además hace commit + push
set -euo pipefail

API="https://1pixel-conteo-api.ai-ffd.workers.dev"
SECRET="${CONTEO_SECRET:?exporta CONTEO_SECRET con la clave admin del Worker antes de correr}"
DIR="$(cd "$(dirname "$0")" && pwd)"
GALLERIES=(3h cecilio calle77 bellavista 5dejulio vereda)

for G in "${GALLERIES[@]}"; do
  out="$DIR/$G.json"
  # Secret va en header, NUNCA en la URL (no se loguea ni queda en el history).
  code=$(curl -s -o "$out.tmp" -w "%{http_code}" -H "X-Admin-Secret: $SECRET" "$API/admin/export?gallery=$G")
  if [ "$code" = "200" ] && python3 -c "import json;d=json.load(open('$out.tmp'));exit(0 if d.get('day_count',0)>0 else 1)" 2>/dev/null; then
    mv "$out.tmp" "$out"
    echo "$G: $(python3 -c "import json;d=json.load(open('$out'));print(d['day_count'],'días', d['first_day'],'->',d['last_day'])")"
  else
    rm -f "$out.tmp"
    echo "$G: sin datos (saltado)"
  fi
done

if [ "${1:-}" = "--push" ]; then
  cd "$DIR/../.."
  git add conteo/archive/*.json
  git commit -m "chore(conteo): respaldo archivo $(date +%Y-%m-%d)" || echo "nada que commitear"
  git push origin main
fi
