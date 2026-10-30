from decimal import Decimal

from utils.validators import validate_email, validate_password, validate_decimal, validate_document, validate_int


def test_email_valido():
    valor, error = validate_email("contacto@vivero.com")
    assert error is None
    assert valor == "contacto@vivero.com"


def test_email_invalido():
    valor, error = validate_email("correo-malo")
    assert valor is None
    assert error


def test_password_corta():
    valor, error = validate_password("123")
    assert valor is None
    assert "8" in error


def test_precio_invalido():
    valor, error = validate_decimal("abc", "precio")
    assert valor is None
    assert error


def test_precio_rechaza_notacion_cientifica_y_simbolos():
    for texto in ("1e5", "2E3", "Infinity", "NaN", "+5", "-5", "1_000", "12.345"):
        valor, error = validate_decimal(texto, "precio")
        assert valor is None, texto
        assert error


def test_precio_valido_con_decimales():
    assert validate_decimal("45000", "precio") == (Decimal("45000"), None)
    assert validate_decimal("12,50", "precio") == (Decimal("12.50"), None)


def test_entero_rechaza_letras():
    for texto in ("1e2", "+3", "1_000", "3.5", "abc"):
        valor, error = validate_int(texto, "cantidad")
        assert valor is None, texto
        assert error


def test_documento_valido():
    valor, error = validate_document("1020304050")
    assert error is None
    assert valor == "1020304050"
