import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")
DOCUMENT_RE = re.compile(r"^[A-Za-z0-9.\-]{5,30}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{4,50}$")
# Solo dígitos: evita notación científica (1e5), signos, guiones bajos e Infinity.
DECIMAL_RE = re.compile(r"^\d{1,10}([.,]\d{1,2})?$")
INT_RE = re.compile(r"^\d{1,9}$")

DOCUMENT_TYPES = ("CC", "CE", "NIT", "Pasaporte", "TI")
CATEGORIES = (
    "Plantas de interior",
    "Plantas de exterior",
    "Suculentas",
    "Cactus",
    "Árboles",
    "Arbustos",
    "Flores",
    "Semillas",
    "Macetas",
    "Abonos",
    "Herramientas",
    "Decoración",
)
CARGOS = (
    "Administrador",
    "Vendedor",
    "Jardinero",
    "Auxiliar de vivero",
    "Contador",
    "Bodeguero",
)
ESTADOS_LABORALES = ("Activo", "Inactivo", "Vacaciones")
ESTADOS_PROVEEDOR = ("Activo", "Inactivo")


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def required(value, field_name):
    text = clean(value)
    if not text:
        return None, f"El campo {field_name} es obligatorio."
    return text, None


def validate_email(value, field_name="correo electrónico"):
    text, error = required(value, field_name)
    if error:
        return None, error
    if not EMAIL_RE.match(text):
        return None, f"Ingrese un {field_name} válido."
    return text.lower(), None


def validate_phone(value):
    text, error = required(value, "teléfono")
    if error:
        return None, error
    if not PHONE_RE.match(text):
        return None, "Ingrese un teléfono válido."
    return text, None


def validate_document(value):
    text, error = required(value, "número de documento")
    if error:
        return None, error
    if not DOCUMENT_RE.match(text):
        return None, "El documento debe tener entre 5 y 30 caracteres alfanuméricos."
    return text.upper(), None


def validate_choice(value, options, field_name):
    text, error = required(value, field_name)
    if error:
        return None, error
    if text not in options:
        return None, f"Seleccione un valor válido para {field_name}."
    return text, None


def validate_decimal(value, field_name, min_value=Decimal("0.01")):
    text, error = required(value, field_name)
    if error:
        return None, error
    if not DECIMAL_RE.match(text):
        return None, f"{field_name} solo admite números (máximo 2 decimales)."
    try:
        number = Decimal(text.replace(",", "."))
    except (InvalidOperation, AttributeError):
        return None, f"{field_name} debe ser un número válido."
    if number < min_value:
        return None, f"{field_name} debe ser mayor o igual a {min_value}."
    return number, None


def validate_int(value, field_name, min_value=0):
    text, error = required(value, field_name)
    if error:
        return None, error
    if not INT_RE.match(text):
        return None, f"{field_name} debe ser un número entero."
    try:
        number = int(text)
    except (TypeError, ValueError):
        return None, f"{field_name} debe ser un número entero."
    if number < min_value:
        return None, f"{field_name} no puede ser menor que {min_value}."
    return number, None


def validate_date(value, field_name):
    text, error = required(value, field_name)
    if error:
        return None, error
    try:
        return datetime.strptime(text, "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"{field_name} no tiene un formato de fecha válido."


def validate_username(value):
    text, error = required(value, "usuario")
    if error:
        return None, error
    if not USERNAME_RE.match(text):
        return None, "El usuario debe tener entre 4 y 50 caracteres (letras, números, punto, guion)."
    return text.lower(), None


def validate_password(value, min_length=8):
    text = value if value is not None else ""
    if len(text) < min_length:
        return None, f"La contraseña debe tener al menos {min_length} caracteres."
    return text, None


def collect_errors(*results):
    errors = []
    values = []
    for value, error in results:
        values.append(value)
        if error:
            errors.append(error)
    return values, errors
