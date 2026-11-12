"""Crea el usuario administrador inicial sin guardar contraseñas en el código."""
import getpass
import os
import sys

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv(os.getenv("ENV_FILE") or None)

from flask import Flask
from config import Config
from database import init_pool, close_connection, DatabaseError
from data import usuarios
from utils.validators import ROL_ADMIN, validate_email, validate_password, validate_username


def _prompt(label, env_name, secret=False):
    value = os.getenv(env_name)
    if value:
        return value
    if secret:
        return getpass.getpass(f"{label}: ")
    return input(f"{label}: ").strip()


def main():
    app = Flask(__name__)
    app.config.from_object(Config)
    with app.app_context():
        try:
            init_pool(app)
        except DatabaseError as exc:
            print(str(exc))
            sys.exit(1)

        username, user_error = validate_username(_prompt("Usuario administrador", "ADMIN_USERNAME"))
        email, email_error = validate_email(_prompt("Correo administrador", "ADMIN_EMAIL"), max_length=100)
        password, pass_error = validate_password(_prompt("Contraseña (mínimo 8 caracteres)", "ADMIN_PASSWORD", secret=True))
        errors = [e for e in (user_error, email_error, pass_error) if e]
        if errors:
            print("No se pudo crear el administrador:")
            for error in errors:
                print(f" - {error}")
            sys.exit(1)

        if usuarios.find_by_username(username):
            print("Ya existe un usuario con ese nombre.")
            sys.exit(1)
        if usuarios.find_by_email(email):
            print("Ya existe un usuario con ese correo.")
            sys.exit(1)

        password_hash = generate_password_hash(password)
        usuarios.create_user(username, email, password_hash, rol=ROL_ADMIN)
        print(f"Administrador '{username}' creado correctamente.")
        close_connection()


if __name__ == "__main__":
    main()
