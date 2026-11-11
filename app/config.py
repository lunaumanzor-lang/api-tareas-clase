"""Configuración de la API, leída de variables de entorno.

La aplicación no guarda configuración en el código: cada ambiente (local,
staging, producción) entrega sus valores al arrancar.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    ambiente: str = "desarrollo"
    version: str = "dev"
    api_token: str | None = None

    @classmethod
    def desde_entorno(cls):
        return cls(
            ambiente=os.environ.get("APP_ENV", "desarrollo"),
            version=os.environ.get("APP_VERSION", "dev"),
            api_token=os.environ.get("API_TOKEN") or None,
        )
