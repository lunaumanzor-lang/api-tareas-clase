"""Almacén de tareas en memoria.

No hay base de datos: las tareas viven mientras el proceso esté en marcha.
"""

TITULO_MAXIMO = 100


class ErrorValidacion(ValueError):
    pass


class AlmacenTareas:
    def __init__(self):
        self._tareas = []
        self._siguiente_id = 1

    def listar(self):
        return list(self._tareas)

    def obtener(self, tarea_id):
        for tarea in self._tareas:
            if tarea["id"] == tarea_id:
                return tarea
        return None

    def crear(self, datos):
        if not isinstance(datos, dict):
            raise ErrorValidacion("El cuerpo debe ser un objeto JSON")
        titulo = datos.get("titulo")
        if not isinstance(titulo, str) or not titulo.strip():
            raise ErrorValidacion("El campo 'titulo' es obligatorio")
        titulo = titulo.strip()
        if len(titulo) > TITULO_MAXIMO:
            raise ErrorValidacion(f"El título admite hasta {TITULO_MAXIMO} caracteres")
        tarea = {"id": self._siguiente_id, "titulo": titulo, "hecha": False}
        self._tareas.append(tarea)
        self._siguiente_id += 1
        return tarea
