from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, g

from utils.validators import ROL_ADMIN


def _usuario_vigente():
    """Confirma en la base que el usuario de la sesión sigue activo y toma su rol actual.

    Así, si el administrador desactiva o cambia el rol de un usuario, el cambio
    se aplica de inmediato y no hasta que esa persona cierre sesión.
    """
    if "usuario_vigente" in g:
        return g.usuario_vigente
    from data import usuarios

    user = usuarios.obtener(session["user_id"])
    vigente = bool(user and user["estado"] == "Activo")
    if vigente:
        session["rol"] = user["rol"]
        session["username"] = user["nombre_usuario"]
        session["email"] = user["email"]
    g.usuario_vigente = vigente
    return vigente


def _exigir_sesion():
    if not session.get("user_id"):
        flash("Debe iniciar sesión para continuar.", "warning")
        return redirect(url_for("auth.login", next=request.path))
    if not _usuario_vigente():
        session.clear()
        flash("Su usuario fue desactivado o eliminado. Inicie sesión de nuevo.", "warning")
        return redirect(url_for("auth.login"))
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        respuesta = _exigir_sesion()
        if respuesta is not None:
            return respuesta
        return view(*args, **kwargs)

    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            respuesta = _exigir_sesion()
            if respuesta is not None:
                return respuesta
            if session.get("rol") not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


# Módulo 3, proveedores y empleados: solo el administrador.
admin_required = roles_required(ROL_ADMIN)


def es_admin():
    return session.get("rol") == ROL_ADMIN


def current_user():
    if not session.get("user_id"):
        return None
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "email": session.get("email"),
        "rol": session.get("rol"),
    }
