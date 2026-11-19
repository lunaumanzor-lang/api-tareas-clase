import json
from pathlib import Path

import pytest

from app import create_app
from app.config import Config

DATOS = Path(__file__).parent / "datos" / "tareas_ejemplo.json"


@pytest.fixture
def tareas_ejemplo():
    return json.loads(DATOS.read_text(encoding="utf-8"))


def test_carga_las_tareas_de_ejemplo(tareas_ejemplo):
    cliente = create_app(Config()).test_client()
    for tarea in tareas_ejemplo:
        assert cliente.post("/tareas", json=tarea).status_code == 201
    assert len(cliente.get("/tareas").get_json()) == len(tareas_ejemplo)
