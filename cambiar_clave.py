"""Cambia la contraseña de un usuario del sistema (por ejemplo, el administrador).

Uso:
    python cambiar_clave.py            # pregunta el usuario y la nueva contraseña
    python cambiar_clave.py admin      # cambia la contraseña del usuario admin

La contraseña no se muestra al escribirla y se guarda cifrada.
También borra los intentos fallidos de esa cuenta para que pueda entrar de inmediato.
"""
import getpass
import os
import sys

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv(os.getenv("ENV_FILE") or None)

from flask import Flask
from config import Config
from database import init_pool, close_connection, execute, DatabaseError
from data import usuarios
from utils.validators import clean, validate_password


def _pedir_clave():
    # NUEVA_CLAVE permite usarlo sin teclado (por ejemplo, en pruebas automáticas)
    valor = os.getenv("NUEVA_CLAVE")
    if valor:
        return valor, valor
    clave = getpass.getpass("Nueva contraseña (mínimo 8 caracteres): ")
    confirmacion = getpass.getpass("Repita la nueva contraseña: ")
    return clave, confirmacion


def main():
    app = Flask(__name__)
    app.config.from_object(Config)
    with app.app_context():
        try:
            init_pool(app)
        except DatabaseError as exc:
            print(str(exc))
            sys.exit(1)

        identificador = clean(sys.argv[1] if len(sys.argv) > 1 else input("Usuario o correo: ")).lower()
        usuario = usuarios.find_by_login(identificador) if identificador else None
        if not usuario:
            print(f"No existe un usuario con el nombre o correo '{identificador}'.")
            sys.exit(1)

        print(f"Usuario: {usuario['nombre_usuario']} ({usuario['email']}) · rol {usuario['rol']} · {usuario['estado']}")
        clave, confirmacion = _pedir_clave()
        _, error = validate_password(clave)
        if error:
            print(error)
            sys.exit(1)
        if clave != confirmacion:
            print("Las contraseñas no coinciden. No se cambió nada.")
            sys.exit(1)

        execute(
            "UPDATE usuarios SET contrasena = %s WHERE id_usuario = %s",
            (generate_password_hash(clave), usuario["id_usuario"]),
        )
        # Desbloquea la cuenta: borra los intentos fallidos por usuario y por correo
        for nombre in {usuario["nombre_usuario"].lower(), usuario["email"].lower()}:
            execute(
                "DELETE FROM intentos_acceso WHERE clave = %s OR clave LIKE %s",
                (f"cuenta:{nombre}", f"%:{nombre}"),
            )
        print(f"Contraseña de '{usuario['nombre_usuario']}' cambiada correctamente.")
        if usuario["estado"] != "Activo":
            print("Ojo: este usuario está Inactivo, así que no podrá entrar hasta que lo activen.")
        close_connection()


if __name__ == "__main__":
    main()
