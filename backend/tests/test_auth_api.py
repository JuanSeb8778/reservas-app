"""Tests de los endpoints /api/auth/*."""

from datetime import timedelta
from http.cookies import SimpleCookie

import pytest
from sqlalchemy import select

from app.core.config import Settings
from app.core.security import create_access_token, create_refresh_token
from app.models import User, UserRole
from tests.conftest import DEFAULT_PASSWORD
from tests.helpers import auth_headers

NEW_USER = {"email": "ana@example.com", "password": "contrasena-segura", "full_name": "Ana Pérez"}


def refresh_cookie(response) -> SimpleCookie:
    """Lee la cabecera Set-Cookie de la respuesta (con sus atributos: Path, HttpOnly...)."""
    cookie = SimpleCookie()
    cookie.load(response.headers["set-cookie"])
    return cookie


def assert_401_bearer(response) -> None:
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


# --- Registro ---


def test_registro_crea_un_cliente_y_devuelve_201_sin_hashed_password(client, db_session):
    response = client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert body["full_name"] == "Ana Pérez"
    assert body["role"] == "client"
    assert set(body) == {"id", "email", "full_name", "role", "created_at"}

    user = db_session.scalar(select(User))
    assert user.hashed_password.startswith("$argon2")


def test_registro_guarda_el_email_en_minusculas_y_sin_espacios(client):
    response = client.post(
        "/api/auth/register", json=NEW_USER | {"email": "  Ana@Example.COM ", "full_name": " Ana "}
    )

    assert response.status_code == 201
    assert response.json()["email"] == "ana@example.com"
    assert response.json()["full_name"] == "Ana"


@pytest.mark.parametrize("email", ["ana@example.com", "ANA@Example.com"])
def test_registro_con_email_duplicado_devuelve_409(client, create_user, email):
    create_user(email="ana@example.com")

    response = client.post("/api/auth/register", json=NEW_USER | {"email": email})

    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe una cuenta con este correo"


def test_registro_detecta_el_duplicado_aunque_falle_la_comprobacion_previa(
    client, create_user, monkeypatch
):
    # Simula una carrera: otra petición creó el usuario justo después de la comprobación.
    create_user(email="ana@example.com")
    monkeypatch.setattr("app.services.auth.get_user_by_email", lambda db, email: None)

    response = client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 409


def test_registro_rechaza_campos_extra_como_role(client, db_session):
    response = client.post("/api/auth/register", json=NEW_USER | {"role": "admin"})

    assert response.status_code == 422
    assert db_session.scalar(select(User)) is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "no-es-un-email"},
        {"password": "corta"},  # menos de 8
        {"password": "x" * 129},  # más de 128
        {"full_name": "   "},
        {"full_name": "x" * 101},
    ],
    ids=["email-invalido", "contrasena-corta", "contrasena-larga", "nombre-vacio", "nombre-largo"],
)
def test_registro_con_datos_invalidos_devuelve_422(client, overrides):
    response = client.post("/api/auth/register", json=NEW_USER | overrides)

    assert response.status_code == 422


# --- Login ---


def test_login_correcto_devuelve_access_token_y_cookie_de_refresco(client, create_user):
    create_user()

    response = client.post(
        "/api/auth/login", json={"email": "ana@example.com", "password": DEFAULT_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"access_token", "token_type", "expires_in"}  # el refresh no va aquí
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 15 * 60
    assert response.headers["cache-control"] == "no-store"

    morsel = refresh_cookie(response)["refresh_token"]
    assert morsel["httponly"] is True
    assert morsel["samesite"] == "lax"
    assert morsel["path"] == "/api/auth"
    assert morsel["max-age"] == str(7 * 24 * 60 * 60)
    assert not morsel["secure"]  # en desarrollo (http://localhost) no puede ser Secure


def test_login_ignora_mayusculas_en_el_email(client, create_user):
    create_user()

    response = client.post(
        "/api/auth/login", json={"email": "ANA@example.com", "password": DEFAULT_PASSWORD}
    )

    assert response.status_code == 200


def test_login_con_contrasena_incorrecta_o_email_inexistente_da_el_mismo_401(client, create_user):
    create_user()

    wrong_password = client.post(
        "/api/auth/login", json={"email": "ana@example.com", "password": "otra-contrasena"}
    )
    unknown_email = client.post(
        "/api/auth/login", json={"email": "nadie@example.com", "password": DEFAULT_PASSWORD}
    )

    for response in (wrong_password, unknown_email):
        assert_401_bearer(response)
        assert response.json()["detail"] == "Correo o contraseña incorrectos"
        assert "set-cookie" not in response.headers


def test_login_con_email_inexistente_verifica_contra_un_hash_ficticio(client, monkeypatch):
    calls = []
    monkeypatch.setattr("app.services.auth.verify_dummy_password", calls.append)

    client.post("/api/auth/login", json={"email": "nadie@example.com", "password": "x"})

    assert calls == ["x"]


def test_login_con_contrasena_gigante_devuelve_422(client):
    response = client.post(
        "/api/auth/login", json={"email": "ana@example.com", "password": "x" * 129}
    )

    assert response.status_code == 422


# --- /me ---


def test_me_con_token_valido_devuelve_el_usuario(client, create_user):
    user = create_user()

    response = client.get("/api/auth/me", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert "hashed_password" not in response.json()


def test_me_sin_token_devuelve_401(client):
    response = client.get("/api/auth/me")

    assert_401_bearer(response)
    assert response.json()["detail"] == "No autenticado"


@pytest.mark.parametrize(
    "authorization",
    ["Bearer no-es-un-jwt", "Basic YW5hOnNlY3JldG8=", "Bearer"],
    ids=["token-malformado", "esquema-basic", "bearer-vacio"],
)
def test_me_con_cabecera_invalida_devuelve_401(client, authorization):
    response = client.get("/api/auth/me", headers={"Authorization": authorization})

    assert_401_bearer(response)


def test_me_con_token_expirado_devuelve_401(client, create_user):
    user = create_user()
    token = create_access_token(user.id, expires_delta=timedelta(seconds=-1))

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert_401_bearer(response)
    assert response.json()["detail"] == "Token inválido o expirado"


def test_me_con_refresh_token_como_bearer_devuelve_401(client, create_user):
    user = create_user()
    token = create_refresh_token(user.id)

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert_401_bearer(response)


def test_me_con_usuario_borrado_despues_de_emitir_el_token_devuelve_401(
    client, create_user, db_session
):
    user = create_user()
    headers = auth_headers(user)
    db_session.delete(user)
    db_session.flush()

    response = client.get("/api/auth/me", headers=headers)

    assert_401_bearer(response)


def test_me_no_recibe_la_cookie_de_refresco(client, create_user):
    # La cookie tiene Path=/api/auth, así que /api/health (fuera de ese path) no la recibe.
    create_user()
    client.post("/api/auth/login", json={"email": "ana@example.com", "password": DEFAULT_PASSWORD})

    request = client.build_request("GET", "/api/health")
    assert "refresh_token" not in request.headers.get("cookie", "")


# --- Refresh ---


def login(client) -> None:
    response = client.post(
        "/api/auth/login", json={"email": "ana@example.com", "password": DEFAULT_PASSWORD}
    )
    assert response.status_code == 200


def test_refresh_con_cookie_valida_devuelve_un_access_token_que_funciona(client, create_user):
    create_user()
    login(client)  # el cliente de pruebas guarda la cookie y la reenvía, como un navegador

    response = client.post("/api/auth/refresh")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "refresh_token" in refresh_cookie(response)  # la cookie se renueva
    token = response.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200


def test_refresh_sin_cookie_devuelve_401(client):
    response = client.post("/api/auth/refresh")

    assert_401_bearer(response)
    assert response.json()["detail"] == "No hay sesión activa"


@pytest.mark.parametrize(
    "make_token",
    [
        lambda user_id: create_access_token(user_id),
        lambda user_id: create_refresh_token(user_id, expires_delta=timedelta(seconds=-1)),
        lambda user_id: "no-es-un-jwt",
    ],
    ids=["access-en-la-cookie", "refresh-expirado", "token-malformado"],
)
def test_refresh_con_cookie_invalida_devuelve_401(client, create_user, make_token):
    user = create_user()
    client.cookies.set("refresh_token", make_token(user.id), path="/api/auth")

    response = client.post("/api/auth/refresh")

    assert_401_bearer(response)
    assert response.json()["detail"] == "Sesión expirada, inicia sesión de nuevo"


def test_refresh_con_usuario_borrado_devuelve_401(client, create_user, db_session):
    user = create_user()
    login(client)
    db_session.delete(user)
    db_session.flush()

    response = client.post("/api/auth/refresh")

    assert_401_bearer(response)


@pytest.mark.parametrize("path", ["/api/auth/refresh", "/api/auth/logout"])
def test_refresh_y_logout_no_aceptan_get(client, path):
    # Con SameSite=Lax el navegador sí envía la cookie en navegaciones GET desde otro sitio;
    # por eso estos endpoints solo aceptan POST.
    assert client.get(path).status_code == 405


# --- Logout ---


def test_logout_borra_la_cookie_y_despues_refresh_devuelve_401(client, create_user):
    create_user()
    login(client)

    response = client.post("/api/auth/logout")

    assert response.status_code == 204
    assert response.content == b""
    morsel = refresh_cookie(response)["refresh_token"]
    assert morsel.value == ""
    assert morsel["max-age"] == "0"
    assert morsel["path"] == "/api/auth"  # mismo path que al crearla, o no se borraría
    assert_401_bearer(client.post("/api/auth/refresh"))


def test_logout_sin_sesion_tambien_devuelve_204(client):
    assert client.post("/api/auth/logout").status_code == 204


# --- Roles ---


def test_el_rol_se_lee_de_la_base_de_datos_y_no_del_token(client, create_user, db_session):
    user = create_user()
    headers = auth_headers(user)
    user.role = UserRole.ADMIN
    db_session.flush()

    response = client.get("/api/auth/me", headers=headers)

    assert response.json()["role"] == "admin"


# --- Casos límite encontrados al intentar romper la API ---


@pytest.mark.parametrize("full_name", ["Ana\x00Pérez", "Ana\nPérez", "Ana\tPérez"])
def test_registro_con_caracteres_de_control_en_el_nombre_devuelve_422(client, full_name):
    # El byte nulo hacía fallar a PostgreSQL con un 500.
    response = client.post("/api/auth/register", json=NEW_USER | {"full_name": full_name})

    assert response.status_code == 422


@pytest.mark.parametrize(
    "password", ["x" * 8, "x" * 128, "ñ" * 128], ids=["8", "128", "128-multibyte"]
)
def test_registro_acepta_contrasenas_en_los_limites(client, password):
    response = client.post("/api/auth/register", json=NEW_USER | {"password": password})

    assert response.status_code == 201


def test_registro_y_login_con_email_unicode(client):
    client.post("/api/auth/register", json=NEW_USER | {"email": "Jörg@Bücher.example"})

    response = client.post(
        "/api/auth/login", json={"email": "JÖRG@bücher.example", "password": NEW_USER["password"]}
    )

    assert response.status_code == 200


@pytest.mark.parametrize("body", [None, [], "texto", {"email": 1, "password": [], "full_name": {}}])
def test_registro_con_cuerpo_que_no_es_el_esperado_devuelve_422(client, body):
    assert client.post("/api/auth/register", json=body).status_code == 422


def test_un_token_con_sub_fuera_de_rango_devuelve_401_y_no_500(client):
    token = create_access_token(2**31)

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert_401_bearer(response)


def test_la_cookie_de_refresco_renovada_mantiene_sus_atributos(client, create_user):
    create_user()
    login(client)

    morsel = refresh_cookie(client.post("/api/auth/refresh"))["refresh_token"]

    assert morsel["httponly"] is True
    assert morsel["samesite"] == "lax"
    assert morsel["path"] == "/api/auth"
    assert morsel["max-age"] == str(7 * 24 * 60 * 60)


def test_en_produccion_la_cookie_es_secure_al_crearla_y_al_borrarla(
    client, create_user, monkeypatch
):
    production = Settings(jwt_secret="x" * 32, environment="production")
    monkeypatch.setattr("app.api.routes.auth.get_settings", lambda: production)
    create_user()

    login_response = client.post(
        "/api/auth/login", json={"email": "ana@example.com", "password": DEFAULT_PASSWORD}
    )
    logout_response = client.post("/api/auth/logout")

    assert refresh_cookie(login_response)["refresh_token"]["secure"] is True
    assert refresh_cookie(logout_response)["refresh_token"]["secure"] is True


def test_openapi_documenta_el_esquema_bearer(client):
    spec = client.get("/openapi.json").json()

    assert spec["components"]["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }
