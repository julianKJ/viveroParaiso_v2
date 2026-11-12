"""Módulo 0: cada rol solo entra a sus módulos (administrador: 1, 2 y 3; vendedor: 1 y 2)."""
import os

os.environ.setdefault("SECRET_KEY", "clave-de-prueba-academica-no-usar-en-produccion")
os.environ.setdefault("MYSQL_PASSWORD", "test")

import pytest

from app import create_app

USUARIOS = {
    1: {"id_usuario": 1, "nombre_usuario": "admin", "email": "admin@vivero.test", "rol": "administrador", "estado": "Activo"},
    2: {"id_usuario": 2, "nombre_usuario": "vendedor1", "email": "v1@vivero.test", "rol": "vendedor", "estado": "Activo"},
    3: {"id_usuario": 3, "nombre_usuario": "inactivo", "email": "x@vivero.test", "rol": "administrador", "estado": "Inactivo"},
}


@pytest.fixture
def app(monkeypatch):
    from data import usuarios, clientes, ventas, productos

    monkeypatch.setattr(usuarios, "obtener", lambda id_usuario: USUARIOS.get(id_usuario))
    monkeypatch.setattr(usuarios, "listar", lambda **kw: ([], 0))
    monkeypatch.setattr(clientes, "listar", lambda **kw: ([], 0))
    monkeypatch.setattr(clientes, "reporte_por_pais", lambda: ([], 0))
    monkeypatch.setattr(ventas, "listar", lambda **kw: ([], 0))
    monkeypatch.setattr(ventas, "resumen_hoy", lambda: {"cantidad": 0, "ingresos": 0})
    monkeypatch.setattr(clientes, "todos", lambda: [])
    monkeypatch.setattr(productos, "disponibles_para_venta", lambda: [])
    aplicacion = create_app()
    aplicacion.config["WTF_CSRF_ENABLED"] = False
    return aplicacion


def _cliente_con_sesion(app, id_usuario):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = id_usuario
        sess["username"] = USUARIOS[id_usuario]["nombre_usuario"]
        sess["rol"] = USUARIOS[id_usuario]["rol"]
    return client


SOLO_ADMIN = ["/usuarios/", "/usuarios/nuevo", "/proveedores/", "/empleados/", "/productos/nuevo"]
AMBOS_ROLES = ["/clientes/", "/clientes/reporte", "/ventas/", "/ventas/nueva"]


@pytest.mark.parametrize("ruta", SOLO_ADMIN)
def test_vendedor_no_entra_a_modulos_de_administrador(app, ruta):
    respuesta = _cliente_con_sesion(app, 2).get(ruta)
    assert respuesta.status_code == 403


@pytest.mark.parametrize("ruta", AMBOS_ROLES)
def test_vendedor_entra_a_clientes_y_ventas(app, ruta):
    respuesta = _cliente_con_sesion(app, 2).get(ruta)
    assert respuesta.status_code == 200


@pytest.mark.parametrize("ruta", AMBOS_ROLES + ["/usuarios/", "/usuarios/nuevo"])
def test_administrador_entra_a_los_tres_modulos(app, ruta):
    respuesta = _cliente_con_sesion(app, 1).get(ruta)
    assert respuesta.status_code == 200


def test_menu_del_vendedor_no_muestra_usuarios(app):
    html = _cliente_con_sesion(app, 2).get("/clientes/").get_data(as_text=True)
    assert "/clientes/" in html and "/ventas/" in html
    assert "/usuarios/" not in html


def test_menu_del_administrador_muestra_usuarios(app):
    html = _cliente_con_sesion(app, 1).get("/clientes/").get_data(as_text=True)
    assert "/usuarios/" in html


def test_usuario_desactivado_pierde_la_sesion(app):
    client = _cliente_con_sesion(app, 3)
    respuesta = client.get("/clientes/", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_rol_cambiado_en_la_base_se_aplica_sin_cerrar_sesion(app):
    # La sesión dice administrador, pero en la base el usuario 2 es vendedor
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["rol"] = "administrador"
    assert client.get("/usuarios/").status_code == 403


def test_reporte_requiere_sesion(app):
    respuesta = app.test_client().get("/clientes/reporte", follow_redirects=False)
    assert respuesta.status_code == 302
