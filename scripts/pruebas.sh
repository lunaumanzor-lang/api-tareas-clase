#!/usr/bin/env bash
# Corre las pruebas de la API. El mismo comando sirve en local y en el pipeline.
set -euo pipefail
python -m pytest "$@"
