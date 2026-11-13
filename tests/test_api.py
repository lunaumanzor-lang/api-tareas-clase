import pytest

from app import create_app
from app.config import Config


@pytest.fixture
def cliente():
    app = create_app(Config())
    return app.test_client()


@pytest.fixture
def cliente_con_token():
    app = create_app(Config(ambiente="staging", version="abc123", api_token="token-de-prueba"))
    return app.test_client()


def test_health_responde_ok(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 201
    assert respuesta.get_json() == {"estado": "ok"}


def test_version_por_defecto(cliente):
    assert cliente.get("/version").get_json() == {"version": "dev", "ambiente": "desarrollo"}


def test_version_refleja_la_configuracion(cliente_con_token):
    assert cliente_con_token.get("/version").get_json() == {
        "version": "abc123",
        "ambiente": "staging",
    }


def test_lista_vacia_al_iniciar(cliente):
    respuesta = cliente.get("/tareas")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_crear_y_listar_tarea(cliente):
    creada = cliente.post("/tareas", json={"titulo": "  Configurar el pipeline  "})
    assert creada.status_code == 201
    assert creada.get_json() == {"id": 1, "titulo": "Configurar el pipeline", "hecha": False}
    assert cliente.get("/tareas").get_json() == [creada.get_json()]


def test_ids_consecutivos(cliente):
    cliente.post("/tareas", json={"titulo": "Primera"})
    segunda = cliente.post("/tareas", json={"titulo": "Segunda"})
    assert segunda.get_json()["id"] == 2


def test_obtener_tarea_existente(cliente):
    cliente.post("/tareas", json={"titulo": "Leer el log"})
    assert cliente.get("/tareas/1").get_json()["titulo"] == "Leer el log"


def test_obtener_tarea_inexistente(cliente):
    assert cliente.get("/tareas/99").status_code == 404


@pytest.mark.parametrize(
    "cuerpo", [{}, {"titulo": ""}, {"titulo": "   "}, {"titulo": 7}, ["no", "objeto"]]
)
def test_rechaza_titulo_invalido(cliente, cuerpo):
    respuesta = cliente.post("/tareas", json=cuerpo)
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_rechaza_cuerpo_que_no_es_json(cliente):
    respuesta = cliente.post("/tareas", data="titulo=hola", content_type="text/plain")
    assert respuesta.status_code == 400


def test_titulo_en_el_limite_se_acepta(cliente):
    assert cliente.post("/tareas", json={"titulo": "x" * 120}).status_code == 201


def test_titulo_demasiado_largo(cliente):
    assert cliente.post("/tareas", json={"titulo": "x" * 121}).status_code == 400


def test_post_sin_token_cuando_se_exige(cliente_con_token):
    assert cliente_con_token.post("/tareas", json={"titulo": "Sin token"}).status_code == 401


def test_post_con_token_incorrecto(cliente_con_token):
    respuesta = cliente_con_token.post(
        "/tareas", json={"titulo": "Mal token"}, headers={"Authorization": "Bearer otro"}
    )
    assert respuesta.status_code == 401


def test_post_con_token_correcto(cliente_con_token):
    respuesta = cliente_con_token.post(
        "/tareas", json={"titulo": "Con token"}, headers={"Authorization": "Bearer token-de-prueba"}
    )
    assert respuesta.status_code == 201


def test_lectura_no_exige_token(cliente_con_token):
    assert cliente_con_token.get("/tareas").status_code == 200


def test_config_desde_entorno(monkeypatch):
    monkeypatch.setenv("APP_ENV", "produccion")
    monkeypatch.setenv("APP_VERSION", "f00dbabe")
    monkeypatch.setenv("API_TOKEN", "secreto")
    cfg = Config.desde_entorno()
    assert (cfg.ambiente, cfg.version, cfg.api_token) == ("produccion", "f00dbabe", "secreto")


def test_config_token_vacio_equivale_a_sin_token(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "")
    assert Config.desde_entorno().api_token is None
