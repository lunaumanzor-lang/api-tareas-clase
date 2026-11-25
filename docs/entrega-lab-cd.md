# Laboratorio de empaquetado y despliegue

<!-- Al terminar, este archivo va al repositorio como docs/entrega-lab-cd.md (consigna del Laboratorio de empaquetado y despliegue, paso 10). -->

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
> | `https://github.com/<usuario>/api-tareas/tree/lab-cd` | `https://github.com/mi-usuario/api-tareas/tree/lab-cd` |
>
> En la vista previa, algunos de esos textos no se muestran, porque se leen como código HTML. En el editor
> siempre se ven.

## 1. Enlaces

| Qué | Enlace |
|---|---|
| Repositorio en el tag `lab-cd` | https://github.com/lunaumanzor-lang/api-tareas-clase/tree/lab-cd |
| Imagen en GHCR con el tag del SHA (paquete con visibilidad pública) | https://github.com/lunaumanzor-lang/api-tareas-clase/pkgs/container/api-tareas-clase |
| Ejecución completa en verde, con la aprobación de producción | https://github.com/lunaumanzor-lang/api-tareas-clase/actions/runs/45523147058 |
| Ejecución con la versión defectuosa: staging en rojo y producción sin correr | https://github.com/lunaumanzor-lang/api-tareas-clase/actions/runs/45527845359 |
| Ejecución del rollback | https://github.com/lunaumanzor-lang/api-tareas-clase/actions/runs/45532151153 |

## 2. Lo que está en el README

La sección **Despliegue y rollback** del `README.md` tiene (marcar con `x` cuando esté):

- [x] El tamaño de la imagen con `python:3.12` y con `python:3.12-slim`, y la elección.
- [x] La justificación de cada línea del `.dockerignore`.
- [x] Cómo saber de qué commit salió una imagen.
- [x] Cuándo conviene el rollback y cómo se lanza.

## 3. Uso de IA

Claude (Anthropic): guía paso a paso del laboratorio, explicación de comandos y apoyo para interpretar los logs y redactar el README y la entrega.