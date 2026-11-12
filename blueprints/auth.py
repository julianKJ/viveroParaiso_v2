from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash

from data import usuarios
from database import DatabaseError
from utils.validators import clean

bp = Blueprint("auth", __name__)


def _attempt_key(identificador):
    # remote_addr ya viene corregida por ProxyFix cuando hay proxy; X-Forwarded-For
    # no se lee directo porque el visitante puede inventarlo para evitar el bloqueo
    ip = request.remote_addr or "unknown"
    return f"{ip}:{identificador.lower()[:120]}"


def _account_key(identificador):
    return f"cuenta:{identificador.lower()[:120]}"


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        identificador = clean(request.form.get("identificador")).lower()
        password = request.form.get("password") or ""

        if not identificador or not password:
            flash("Ingrese usuario o correo y contraseña.", "error")
            return render_template("login.html")

        clave = _attempt_key(identificador)
        clave_cuenta = _account_key(identificador)
        try:
            if usuarios.is_locked(clave) or usuarios.is_locked(clave_cuenta):
                flash(
                    "Demasiados intentos fallidos. Espere unos minutos e inténtelo de nuevo.",
                    "error",
                )
                return render_template("login.html")

            user = usuarios.find_by_login(identificador)
            if (
                not user
                or user.get("estado") != "Activo"
                or not check_password_hash(user["contrasena"], password)
            ):
                locked = usuarios.register_failed_attempt(
                    clave,
                    current_app.config["MAX_LOGIN_ATTEMPTS"],
                    current_app.config["LOGIN_LOCK_MINUTES"],
                )
                locked = usuarios.register_failed_attempt(
                    clave_cuenta,
                    current_app.config["MAX_ACCOUNT_ATTEMPTS"],
                    current_app.config["LOGIN_LOCK_MINUTES"],
                ) or locked
                if locked:
                    flash(
                        "La cuenta de acceso quedó temporalmente bloqueada por intentos fallidos.",
                        "error",
                    )
                else:
                    flash("Credenciales incorrectas. Verifique los datos e inténtelo de nuevo.", "error")
                return render_template("login.html")

            usuarios.clear_attempts(clave)
            usuarios.clear_attempts(clave_cuenta)
            session.clear()
            session.permanent = True
            session["user_id"] = user["id_usuario"]
            session["username"] = user["nombre_usuario"]
            session["email"] = user["email"]
            session["rol"] = user["rol"]
            flash(f"Bienvenido, {user['nombre_usuario']}.", "success")
            destino = request.args.get("next") or url_for("dashboard.index")
            if not destino.startswith("/"):
                destino = url_for("dashboard.index")
            return redirect(destino)
        except DatabaseError:
            flash("No fue posible validar el acceso. Revise la conexión a MySQL.", "error")

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))
