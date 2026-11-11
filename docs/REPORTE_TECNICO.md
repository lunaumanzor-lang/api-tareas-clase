# Reporte técnico - Pipeline CI/CD de la API de tareas

> Autor o autora: (nombre) · Repositorio: (URL) · Tag entregado: (tag)

## 1. Resumen

Tres a cinco líneas: qué hace el pipeline, de dónde sale un cambio y dónde termina.

## 2. Flujo del pipeline

El diagrama Mermaid actualizado (puede partir de `docs/mapa-cicd.md`): jobs, dependencias entre
ellos, environments y el punto de aprobación.

## 3. Etapas y decisiones

| Etapa o job | Qué hace | Qué lo dispara | Decisión técnica y alternativa descartada |
|---|---|---|---|
| | | | |

## 4. Configuración, variables y secretos

Solo nombres, nunca valores.

| Nombre | Tipo (variable o secreto) | Environment | Para qué sirve |
|---|---|---|---|
| | | | |

Permisos del `GITHUB_TOKEN` por job y por qué.

## 5. Evidencia

| Evidencia | Enlace |
|---|---|
| Ejecución completa en verde (con aprobación de producción) | |
| Imagen en GHCR con el tag del SHA | |
| Ejecución con un fallo detenido por el pipeline | |
| Ejecución del rollback | |
| Pull request de un cambio que recorrió todo el flujo | |

## 6. Fallos diagnosticados

Al menos uno: síntoma (líneas del log como texto), causa, corrección y control que lo evita ahora.

## 7. Mejoras pendientes

Lo próximo que se agregaría al pipeline y qué riesgo atiende.

## 8. Uso de herramientas de IA

Qué herramienta se usó y para qué. Una línea por uso.
