# Laboratorio de integración continua

<!-- Al terminar, este archivo va al repositorio como docs/diagnostico-ci.md (guía de laboratorio del Tema 3, Parte 3). -->

> **Cómo completar esta plantilla**
>
> Cada texto que está entre los signos **menor que** y **mayor que** se reemplaza por lo que se pide,
> incluidos los dos signos. El resto queda como está.
>
> | Signo | Nombre |
> |:---:|---|
> | `<` | menor que |
> | `>` | mayor que |
>
> Ejemplo, con `mi-usuario` en lugar del usuario de GitHub:
>
> | En la plantilla | Ya completado |
> |---|---|
> | `https://github.com/<usuario>/api-tareas/tree/lab-ci` | `https://github.com/mi-usuario/api-tareas/tree/lab-ci` |
>
> En la vista previa, algunos de esos textos no se muestran, porque se leen como código HTML. En el editor
> siempre se ven.

## 1. Enlaces

| Qué | Enlace |
|---|---|
| Repositorio en el tag `lab-ci` | https://github.com/lunaumanzor-lang/api-tareas-clase/tree/lab-ci |
| Pull request que el check bloqueó (prueba rota a propósito) | https://github.com/lunaumanzor-lang/api-tareas-clase/pull/5 |

## 2. Diagnóstico de los tres pipelines rotos

### Caso 1

**Síntoma** (el paso que falló primero y su mensaje, copiado del log como texto):

```text
Paso que falló primero: Pruebas
/opt/hostedtoolcache/Python/3.12.16/x64/bin/python: No module named pytest
Error: Process completed with exit code 1.
```

**Causa:** En .github/workflows/ci.yml, el paso "Instalar dependencias" instala requirements.txt en lugar de requirements-dev.txt. requirements.txt solo trae las dependencias de la app (Flask, gunicorn), no pytest, así que el paso Pruebas no encuentra pytest.

**Corrección:** En .github/workflows/ci.yml, el paso "Instalar dependencias" vuelve a instalar requirements-dev.txt, que incluye requirements.txt más pytest. · Commit: https://github.com/lunaumanzor-lang/api-tareas-clase/pull/6/commits/12bfca3c684cbbae12a72f988e533920a368e518

**Prevención:** Verificar en el mismo paso "Instalar dependencias" que las herramientas de prueba quedaron instaladas (agregar `python -m pytest --version` después del pip install). Así, si se instala el archivo de requisitos equivocado, el pipeline falla en ese paso con un mensaje claro, en vez de fallar después en Pruebas.

### Caso 2

**Síntoma** (el paso que falló primero y su mensaje, copiado del log como texto):

```text
Paso que falló primero: Publicar reporte de pruebas (los pasos anteriores, incluido Pruebas, pasaron)
Error: No files were found with the provided path: reporte/. No artifacts will be uploaded.
```

**Causa:** En .github/workflows/ci.yml, el paso "Publicar reporte de pruebas" usa path: reporte/ (sin "s"), pero scripts/pruebas.sh deja el reporte en reportes/junit.xml. Como la carpeta reporte/ no existe y el paso tiene if-no-files-found: error, falla.

**Corrección:** En .github/workflows/ci.yml, el paso "Publicar reporte de pruebas" vuelve a usar path: reportes/, la carpeta donde scripts/pruebas.sh deja junit.xml. · Commit: https://github.com/lunaumanzor-lang/api-tareas-clase/pull/7/commits/f8705d760bb0946a8ed50421f60ef2ef925785f8

**Prevención:** Definir la carpeta de reportes en un solo lugar (una variable REPORTES_DIR en el workflow, que usen tanto scripts/pruebas.sh como el paso de publicar), para que no puedan quedar desalineadas. Mantener if-no-files-found: error, que hace que el problema se note en el pull request en vez de pasar en silencio.

### Caso 3

**Síntoma** (el paso que falló primero y su mensaje, copiado del log como texto):

```text
Paso que falló primero: Pruebas
ERROR tests/test_datos_ejemplo.py::test_carga_las_tareas_de_ejemplo - FileNotFoundError: [Errno 2] No such file or directory: '/home/runner/work/api-tareas-clase/api-tareas-clase/tests/datos/tareas_ejemplo.json'
22 passed, 1 error
Error: Process completed with exit code 1.
```

**Causa:** El .gitignore del caso agrega la regla *.json (línea 13), pensada para los reportes de cobertura. Esa regla también ignora tests/datos/tareas_ejemplo.json, así que el archivo nunca se agregó al commit ni llegó a GitHub; en el Codespace existe, pero en el runner no, y la prueba test_carga_las_tareas_de_ejemplo no lo encuentra. Se confirma con: git check-ignore -v tests/datos/tareas_ejemplo.json

**Corrección:** En .gitignore se cambió la regla *.json por coverage.json, para ignorar solo el reporte de cobertura, y se agregó al commit tests/datos/tareas_ejemplo.json, que nunca se había subido. · Commit: https://github.com/lunaumanzor-lang/api-tareas-clase/pull/8/commits/b4d258da2e9ebff9859eb1375e3d33b25fdceefb

**Prevención:** Escribir reglas de .gitignore específicas, partiendo de una plantilla estándar (por ejemplo, la de Python de github/gitignore), en lugar de comodines amplios como *.json. Revisar en el diff del pull request cualquier cambio al .gitignore y, antes de hacer commit, comprobar con git status --ignored que ningún archivo necesario quedó ignorado.

## 3. Uso de IA

Claude (Anthropic): guía paso a paso del laboratorio, explicación de comandos y apoyo para interpretar los logs y redactar el diagnóstico.