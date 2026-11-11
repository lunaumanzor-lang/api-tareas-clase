"""API de tareas: la aplicación de laboratorio del curso."""

import hmac
import logging

from flask import Flask, jsonify, request

from .config import Config
from .tareas import AlmacenTareas, ErrorValidacion

log = logging.getLogger("api_tareas")


def create_app(config=None):
    cfg = config or Config.desde_entorno()
    app = Flask(__name__)
    almacen = AlmacenTareas()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    log.info(
        "Iniciando API de tareas version=%s ambiente=%s token_configurado=%s",
        cfg.version,
        cfg.ambiente,
        "si" if cfg.api_token else "no",
    )

    def autorizado():
        if not cfg.api_token:
            return True
        enviado = request.headers.get("Authorization", "")
        return hmac.compare_digest(enviado, f"Bearer {cfg.api_token}")

    @app.after_request
    def registrar(respuesta):
        log.info("%s %s -> %s", request.method, request.path, respuesta.status_code)
        return respuesta

    @app.get("/health")
    def health():
        return jsonify(estado="ok")

    @app.get("/version")
    def version():
        return jsonify(version=cfg.version, ambiente=cfg.ambiente)

    @app.get("/tareas")
    def listar_tareas():
        return jsonify(almacen.listar())

    @app.get("/tareas/<int:tarea_id>")
    def obtener_tarea(tarea_id):
        tarea = almacen.obtener(tarea_id)
        if tarea is None:
            return jsonify(error="Tarea no encontrada"), 404
        return jsonify(tarea)

    @app.post("/tareas")
    def crear_tarea():
        if not autorizado():
            return jsonify(error="No autorizado"), 401
        try:
            tarea = almacen.crear(request.get_json(silent=True))
        except ErrorValidacion as error:
            return jsonify(error=str(error)), 400
        return jsonify(tarea), 201

    return app
