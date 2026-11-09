from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash

from data import usuarios
from database import DatabaseError
from utils.validators import clean

bp = Blueprint("auth", __name__)


def _attempt_key(identificador):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    return f"{ip}:{identificador.lower()}"


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
        try:
            if usuarios.is_locked(clave):
                flash(
                    "Demasiados intentos fallidos. Espere unos minutos e inténtelo de nuevo.",
                    "error",
                )
                return render_template("login.html")

            user = usuarios.find_by_login(identificador)
            if (
                not user
                or not user.get("activo")
                or not check_password_hash(user["password_hash"], password)
            ):
                locked = usuarios.register_failed_attempt(
                    clave,
                    current_app.config["MAX_LOGIN_ATTEMPTS"],
                    current_app.config["LOGIN_LOCK_MINUTES"],
                )
                if locked:
                    flash(
                        "La cuenta de acceso quedó temporalmente bloqueada por intentos fallidos.",
                        "error",
                    )
                else:
                    flash("Credenciales incorrectas. Verifique los datos e inténtelo de nuevo.", "error")
                return render_template("login.html")

            usuarios.clear_attempts(clave)
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            session["rol"] = user["rol"]
            flash(f"Bienvenido, {user['username']}.", "success")
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
