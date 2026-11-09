"""Tests de hash de contraseñas y tokens JWT (sin base de datos ni HTTP)."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def encode(payload: dict, secret: str | None = None, algorithm: str = "HS256") -> str:
    """Firma un payload a mano, para fabricar tokens raros que la app nunca emitiría."""
    return jwt.encode(payload, secret or get_settings().jwt_secret, algorithm=algorithm)


def valid_payload(**overrides) -> dict:
    now = datetime.now(UTC)
    return {"sub": "1", "type": "access", "iat": now, "exp": now + timedelta(minutes=5)} | overrides


# --- Contraseñas ---


def test_el_hash_es_argon2_y_no_contiene_la_contrasena():
    hashed = hash_password("mi-contrasena")

    assert hashed.startswith("$argon2")
    assert "mi-contrasena" not in hashed


def test_verificar_contrasena_correcta_e_incorrecta():
    hashed = hash_password("mi-contrasena")

    assert verify_password("mi-contrasena", hashed) is True
    assert verify_password("otra-contrasena", hashed) is False


def test_dos_hashes_de_la_misma_contrasena_son_distintos():
    # Cada hash lleva una "sal" aleatoria: dos usuarios con la misma contraseña no comparten hash.
    assert hash_password("mi-contrasena") != hash_password("mi-contrasena")


# --- Tokens ---


def test_access_token_lleva_sub_como_texto_type_iat_y_exp():
    token = create_access_token(42)

    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["exp"] - payload["iat"] == 15 * 60


def test_decode_token_devuelve_el_id_del_usuario():
    assert decode_token(create_access_token(42), "access") == 42
    assert decode_token(create_refresh_token(42), "refresh") == 42


def test_decode_rechaza_un_token_del_tipo_equivocado():
    with pytest.raises(TokenError):
        decode_token(create_refresh_token(42), "access")
    with pytest.raises(TokenError):
        decode_token(create_access_token(42), "refresh")


def test_decode_rechaza_un_token_expirado():
    token = create_access_token(42, expires_delta=timedelta(seconds=-1))

    with pytest.raises(TokenError):
        decode_token(token, "access")


def test_decode_rechaza_un_token_firmado_con_otra_clave():
    token = encode(valid_payload(), secret="otra-clave-de-al-menos-32-caracteres-xx")

    with pytest.raises(TokenError):
        decode_token(token, "access")


def test_decode_rechaza_un_token_manipulado():
    header, payload, signature = create_access_token(42).split(".")
    # Se cambia el payload por el de otro usuario sin volver a firmar.
    forged_payload = encode(valid_payload(sub="1")).split(".")[1]

    with pytest.raises(TokenError):
        decode_token(f"{header}.{forged_payload}.{signature}", "access")


def test_decode_rechaza_un_token_sin_firma_alg_none():
    token = jwt.encode(valid_payload(), key=None, algorithm="none")

    with pytest.raises(TokenError):
        decode_token(token, "access")


@pytest.mark.parametrize("claim", ["sub", "type", "exp", "iat"])
def test_decode_rechaza_un_token_al_que_le_falta_un_claim(claim):
    payload = valid_payload()
    del payload[claim]

    with pytest.raises(TokenError):
        decode_token(encode(payload), "access")


def test_decode_rechaza_un_sub_que_no_es_un_numero():
    with pytest.raises(TokenError):
        decode_token(encode(valid_payload(sub="admin")), "access")


@pytest.mark.parametrize("token", ["", "no-es-un-jwt", "a.b.c"])
def test_decode_rechaza_texto_que_no_es_un_jwt(token):
    with pytest.raises(TokenError):
        decode_token(token, "access")


@pytest.mark.parametrize(
    "sub",
    ["0", "-1", "1.0", " 1", "1_0", "١", "2147483648", "9" * 30],
    ids=[
        "cero",
        "negativo",
        "decimal",
        "espacio",
        "guion-bajo",
        "digito-arabe",
        "int4+1",
        "enorme",
    ],
)
def test_decode_rechaza_un_sub_fuera_de_los_ids_validos(sub):
    # "2147483648" no cabe en una columna INTEGER: antes llegaba a la consulta y daba un 500.
    with pytest.raises(TokenError):
        decode_token(encode(valid_payload(sub=sub)), "access")


# PyJWT avisa de que la clave de tests es corta para HS512; aquí da igual, se rechaza antes.
@pytest.mark.filterwarnings("ignore:The HMAC key")
def test_decode_rechaza_otro_algoritmo_aunque_la_clave_sea_correcta():
    with pytest.raises(TokenError):
        decode_token(encode(valid_payload(), algorithm="HS512"), "access")
