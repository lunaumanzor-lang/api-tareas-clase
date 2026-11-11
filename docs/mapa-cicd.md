# Mapa de estrategia CI/CD - API de tareas

> Autor o autora: (nombre)
> Punto de partida: `docs/DESPLIEGUE_MANUAL.md`, el proceso manual que el pipeline va a reemplazar.
> Cómo se ve un mapa terminado: `docs/ejemplo-mapa-cicd-sitio.md` (otro caso, mismo método).
> Sintaxis de los diagramas: la Guía rápida de Mermaid (Moodle, material de apoyo).

## 1. Flujo de commit a producción

Reemplazar este esqueleto por el flujo completo: etapas, ambientes y los puntos donde decide una
persona. GitHub y la vista previa de VS Code (`Ctrl+Shift+V`) muestran el diagrama. Si queda muy
ancho, cambiar `LR` por `TD`.

```mermaid
flowchart LR
    A[Cambio en una rama] --> B[Pull request]
```

## 2. Ambientes

| Ambiente | Para qué sirve | Cómo llega un cambio | Quién decide que llegue |
|---|---|---|---|
| | | | |

## 3. Riesgos del proceso manual y controles

Un renglón por riesgo. La columna "Paso" cita el paso de `DESPLIEGUE_MANUAL.md`.

| Paso | Riesgo | Qué puede pasar | Control del pipeline que lo atiende | Etapa del flujo |
|---|---|---|---|---|
| | | | | |

## 4. Criterios de éxito

Qué tiene que ser verdad para decir que un despliegue salió bien, de forma que una máquina lo
pueda comprobar.

-

## 5. Decisiones y preguntas abiertas

-
