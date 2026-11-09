import os

os.environ.setdefault("SECRET_KEY", "clave-de-prueba-academica-no-usar-en-produccion")
os.environ.setdefault("MYSQL_PASSWORD", "test")

from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app


def test_password_no_queda_en_texto_plano():
    texto = "ClaveSegura123"
    hashed = generate_password_hash(texto)
    assert hashed != texto
    assert check_password_hash(hashed, texto)


def test_login_get_disponible():
    app = create_app()
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    assert "Iniciar sesión".encode("utf-8") in response.data


def test_dashboard_requiere_autenticacion():
    app = create_app()
    client = app.test_client()
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_empleados_requiere_autenticacion():
    app = create_app()
    client = app.test_client()
    response = client.get("/empleados/", follow_redirects=False)
    assert response.status_code == 302


def test_no_existe_acceso_fijo_admin123(monkeypatch):
    # Sin usuario en la base, admin/admin123 no debe abrir sesión
    from data import usuarios

    monkeypatch.setattr(usuarios, "is_locked", lambda clave: False)
    monkeypatch.setattr(usuarios, "find_by_login", lambda identificador: None)
    monkeypatch.setattr(usuarios, "register_failed_attempt", lambda *args: False)

    app = create_app()
    app.config["WTF_CSRF_ENABLED"] = False
    client = app.test_client()
    response = client.post(
        "/login",
        data={"identificador": "admin", "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"admin123" not in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def _intentos_en_memoria(monkeypatch):
    """Reemplaza la tabla intentos_acceso por un diccionario con la misma lógica."""
    from datetime import datetime, timedelta
    from data import usuarios

    tabla = {}

    def is_locked(clave):
        hasta = tabla.get(clave, {}).get("hasta")
        return bool(hasta and hasta > datetime.now())

    def register_failed_attempt(clave, max_attempts, lock_minutes):
        fila = tabla.setdefault(clave, {"n": 0, "hasta": None})
        fila["n"] += 1
        if fila["n"] >= max_attempts:
            fila["n"] = 0
            fila["hasta"] = datetime.now() + timedelta(minutes=lock_minutes)
            return True
        return False

    monkeypatch.setattr(usuarios, "is_locked", is_locked)
    monkeypatch.setattr(usuarios, "register_failed_attempt", register_failed_attempt)
    monkeypatch.setattr(usuarios, "find_by_login", lambda identificador: None)
    return tabla


def _intentar(client, ip_falsa):
    return client.post(
        "/login",
        data={"identificador": "admin", "password": "incorrecta1"},
        headers={"X-Forwarded-For": ip_falsa},
    )


def test_ip_falsa_no_evita_el_bloqueo(monkeypatch):
    tabla = _intentos_en_memoria(monkeypatch)
    app = create_app()
    app.config["WTF_CSRF_ENABLED"] = False
    client = app.test_client()
    for i in range(5):
        _intentar(client, f"10.0.0.{i}")
    # Las 5 IPs inventadas cuentan como la misma IP real, que queda bloqueada
    assert not any(clave.startswith("10.0.0.") for clave in tabla)
    respuesta = _intentar(client, "10.0.0.99")
    assert "Demasiados intentos".encode("utf-8") in respuesta.data


def test_bloqueo_por_cuenta_aunque_cambie_la_ip(monkeypatch):
    _intentos_en_memoria(monkeypatch)
    app = create_app()
    app.config["WTF_CSRF_ENABLED"] = False
    # Simula un atacante con muchas IPs reales: el tope por IP no lo frena, el de la cuenta sí
    app.config["MAX_LOGIN_ATTEMPTS"] = 1000
    client = app.test_client()
    for i in range(15):
        _intentar(client, f"203.0.113.{i}")
    respuesta = _intentar(client, "203.0.113.200")
    assert "Demasiados intentos".encode("utf-8") in respuesta.data
