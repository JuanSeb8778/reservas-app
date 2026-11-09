"""Tests de la configuración relacionada con la autenticación."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_rechaza_un_jwt_secret_de_menos_de_32_caracteres():
    with pytest.raises(ValidationError, match="jwt_secret"):
        Settings(jwt_secret="corta")


@pytest.mark.parametrize(("environment", "secure"), [("development", False), ("production", True)])
def test_la_cookie_solo_es_secure_fuera_de_desarrollo(environment, secure):
    settings = Settings(jwt_secret="x" * 32, environment=environment)

    assert settings.cookie_secure is secure
