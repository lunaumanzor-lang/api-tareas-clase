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

## Imagen de contenedor

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