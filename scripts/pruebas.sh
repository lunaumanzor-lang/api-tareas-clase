#!/usr/bin/env bash
# Corre las pruebas de la API. El mismo comando sirve en local y en el pipeline.
# Deja el reporte JUnit en reportes/junit.xml.
set -euo pipefail
mkdir -p reportes
python -m pytest --junitxml=reportes/junit.xml "$@"
