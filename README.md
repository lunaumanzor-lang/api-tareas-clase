# API de tareas

Aplicación de laboratorio del curso SOFT-756 (Implementación de CI/CD y Prácticas DevOps). Es una
API pequeña en Python (Flask) que guarda tareas en memoria. El código de la aplicación casi no
cambia durante el curso: lo que crece es el **pipeline** que la construye, la prueba, la empaqueta
y la despliega.

## Endpoints

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/health` | `{"estado": "ok"}` si la API está viva |
| GET | `/version` | Versión desplegada y ambiente (`APP_VERSION`, `APP_ENV`) |
| GET | `/tareas` | Lista de tareas |
| GET | `/tareas/<id>` | Una tarea, o 404 |
| POST | `/tareas` | Crea una tarea con `{"titulo": "..."}`; 201, o 400 si el título no es válido |

Si la variable `API_TOKEN` tiene valor, `POST /tareas` exige el encabezado
`Authorization: Bearer <token>`. Las lecturas no lo exigen.

## Configuración

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `APP_ENV` | Nombre del ambiente (desarrollo, staging, produccion) | `desarrollo` |
| `APP_VERSION` | Versión que reporta `/version` | `dev` |
| `API_TOKEN` | Token que protege `POST /tareas` | sin valor (no se exige) |

## Correr en local

Requisitos: Python 3.10 o posterior, Git y una terminal Bash (en Windows, **Git Bash**).

```bash
python -m venv .venv
source .venv/bin/activate          # en Windows (Git Bash): source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
bash scripts/pruebas.sh            # corre las pruebas
python -m flask --app app run --port 8000
```

Con la API en marcha, en otra terminal:

```bash
bash scripts/smoke.sh http://localhost:8000
```

Resultado esperado:

```text
Smoke test contra http://localhost:8000
OK /health
OK /version -> {"ambiente":"desarrollo","version":"dev"}
OK /tareas
Smoke test superado
```

## Estructura

```text
app/            código de la API (config.py lee las variables de entorno)
tests/          pruebas con pytest
scripts/        pruebas.sh y smoke.sh: los mismos comandos en local y en el pipeline
docs/           documentación del flujo de entrega
requirements.txt       dependencias de la aplicación, con versión fija
requirements-dev.txt   dependencias para desarrollar y probar
```

## Despliegue y rollback

El pipeline (`.github/workflows/ci-cd.yml`) construye la imagen **una sola vez**, en el job
`empaquetar`, y la publica en GHCR solo cuando el cambio llega a `main` (en los pull request corre
solo CI). Cada imagen se identifica con el SHA del commit del que salió:

```text
ghcr.io/lunaumanzor-lang/api-tareas-clase:<SHA del commit>
```

### Por qué cada línea del `.dockerignore`

El `.dockerignore` decide qué parte del repositorio **no** entra al contexto de `docker build`, y
por lo tanto no puede terminar dentro de la imagen.

| Línea | Qué pasaría si entrara a la imagen |
|---|---|
| `.git` | Se copiaría todo el historial del repositorio: la imagen crece sin necesidad y expone commits viejos, que podrían contener información sensible. |
| `.github` | Los workflows del pipeline no los usa la API; solo agregan peso y revelan cómo se construye y publica. |
| `.venv`, `venv` | Un entorno virtual local, armado para otra máquina y otro sistema operativo, que puede chocar con las dependencias instaladas en la imagen y la hace mucho más pesada. |
| `**/__pycache__`, `**/*.pyc` | Bytecode compilado en la máquina de quien construye: es basura, ocupa espacio y puede no corresponder al código copiado. |
| `.pytest_cache`, `.ruff_cache` | Cachés de las herramientas de desarrollo; no sirven en producción. |
| `.coverage`, `htmlcov` | Resultados de cobertura de pruebas locales; no aportan nada a la API en ejecución. |
| `reportes` | Reportes JUnit de pruebas locales; se publican como artefacto del pipeline, no van en la imagen. |
| `tests` | Las pruebas se corren en el job `ci`, antes de empaquetar; dentro de la imagen solo agregan código que no se ejecuta. |
| `docs` | Documentación para personas; la API no la lee. |
| `.env` | Puede tener secretos (tokens, contraseñas). Si entrara, cualquiera que descargue la imagen pública podría leerlos. |

### Base de la imagen: `python:3.12` vs `python:3.12-slim`

Se construyó la misma API con las dos bases y se anotó lo que muestra `docker image ls` en el job
**Empaquetar imagen**:

| Base | Tamaño en disco (DISK USAGE) | Tamaño de descarga (CONTENT SIZE) |
|---|---|---|
| `python:3.12` | 1.61 GB | 414 MB |
| `python:3.12-slim` | 188 MB | 45.5 MB |

**Elección: `python:3.12-slim`.** Es unas 9 veces más liviana y la API funciona igual (el smoke test
pasa con las dos). Una imagen más chica se descarga más rápido en cada despliegue, ocupa menos
espacio en el registro y en los servidores, y trae menos paquetes del sistema que puedan tener
vulnerabilidades. La base completa incluye compiladores y herramientas de desarrollo que esta API
no necesita.

### Cómo saber de qué commit salió una imagen

Hay tres formas, y las tres deben coincidir:

1. **El tag de la imagen** es el SHA completo del commit:
   `ghcr.io/lunaumanzor-lang/api-tareas-clase:7a021c84...` salió del commit `7a021c84...`.
2. **La etiqueta `org.opencontainers.image.revision`**, que el pipeline agrega al construir
   (`--label org.opencontainers.image.revision="$GITHUB_SHA"`). Sirve aunque la imagen se haya
   re-etiquetado con otro nombre:

   ```bash
   docker pull ghcr.io/lunaumanzor-lang/api-tareas-clase:<tag>
   docker inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' \
     ghcr.io/lunaumanzor-lang/api-tareas-clase:<tag>
   ```

   La etiqueta `org.opencontainers.image.source` indica el repositorio, así que con las dos se
   llega al commit exacto en GitHub.
3. **El endpoint `/version`** de la API en ejecución responde con `APP_VERSION`, que el pipeline
   fija con `--build-arg APP_VERSION="$GITHUB_SHA"`.

   ### Esquema de tags de la imagen

| Cuándo | Tags que se publican | Ejemplo |
|---|---|---|
| Cada merge a `main` | Solo el SHA del commit | `ghcr.io/lunaumanzor-lang/api-tareas-clase:c17339b...` |
| Al subir un tag de Git que empieza con `v` | El SHA del commit **y** el nombre del tag | `...:<SHA>` y `...:v0.1.0` |

Los dos tags apuntan a **la misma imagen**: el paso **Publicar tag legible** no la vuelve a construir,
solo le agrega un segundo nombre con `docker tag` y lo sube con `docker push`. El SHA sirve para
rastrear exactamente de qué commit salió; el tag legible (`v0.1.0`) sirve para que las personas
hablen de versiones y para desplegar una versión concreta sin copiar un SHA de 40 caracteres.

Para publicar una versión:

```bash
git switch main && git pull
git tag v0.1.0
git push origin v0.1.0
```

### Despliegue en staging y producción

Después de `empaquetar`, el pipeline despliega **la misma imagen** (la que tiene el SHA del commit) en
dos environments de GitHub:

1. **staging** (job `staging`): arranca el contenedor con
   `docker run -d --name api -p 8080:8000 -e APP_ENV=staging <imagen>` y corre
   `bash scripts/smoke.sh http://localhost:8080`. Si el smoke test falla, el job queda en rojo y
   producción no corre.
2. **produccion** (job `produccion`, `needs: [empaquetar, staging]`): el environment tiene un revisor
   obligatorio, así que el job espera a que alguien apruebe en **Review deployments**. Después hace el
   mismo `docker run` (con `APP_ENV=produccion`) y el mismo smoke test.

Las pruebas unitarias de CI no ven el contenedor: un error de configuración del despliegue (por ejemplo,
cambiar el `--bind` del `CMD` al puerto 5000) pasa CI y solo lo detecta el smoke test en staging.

### Rollback: cuándo conviene y cómo se lanza

**Cuándo conviene:** cuando una versión ya integrada en `main` falla al desplegarse (staging en rojo) o
causa un problema después de desplegada, y hace falta **volver rápido a una versión que funcionaba**
mientras se prepara la corrección. El rollback no arregla el código: vuelve a desplegar una imagen
anterior, que ya está construida y probada en GHCR, sin reconstruir nada. La corrección definitiva se
hace después **hacia adelante**, con `git revert` del commit defectuoso, por pull request, y se lleva a
producción con aprobación.

**Cómo se lanza** (workflow `.github/workflows/rollback.yml`, solo manual):

1. Tener el SHA **completo** (40 caracteres) del último commit bueno de `main`. Conviene anotarlo
   antes de integrar un cambio riesgoso: `git switch main && git pull && git log -1 --format=%H`.
   También se puede sacar del tag de la imagen en GHCR o del `/version` de la API.
2. En GitHub: **Actions → Rollback → Run workflow**, rama `main`, pegar el SHA y **Run workflow**.
3. El workflow valida que el SHA tenga 40 caracteres hexadecimales en minúsculas, despliega en
   staging la imagen `ghcr.io/lunaumanzor-lang/api-tareas-clase:<SHA>` y corre el smoke test.

**Ejemplo en este repositorio:** el PR #15 cambió el `--bind` a `0.0.0.0:5000`; CI pasó, pero staging
falló en el smoke test y producción no corrió. El rollback con el SHA `af97d9367ff49dae9152c724de2711ad568e4059`
volvió a desplegar la versión anterior con el smoke test en verde. Después, el PR #17 hizo
`git revert` del commit `d29f2b2` y la corrección llegó a producción con aprobación.