#!/usr/bin/env bash
# Smoke test: comprueba que una instancia en marcha de la API responde.
# Uso: scripts/smoke.sh [URL]   (por defecto http://localhost:8000)
set -euo pipefail
URL="${1:-http://localhost:8000}"

falla() {
  echo "SMOKE FALLO: $1"
  exit 1
}

echo "Smoke test contra $URL"

salud=$(curl -fsS --retry 15 --retry-delay 2 --retry-all-errors "$URL/health") \
  || falla "/health no responde"
echo "$salud" | grep -Eq '"estado": ?"ok"' || falla "/health respondio: $salud"
echo "OK /health"

version=$(curl -fsS "$URL/version") || falla "/version no responde"
echo "OK /version -> $version"

curl -fsS -o /dev/null "$URL/tareas" || falla "/tareas no responde"
echo "OK /tareas"

echo "Smoke test superado"
