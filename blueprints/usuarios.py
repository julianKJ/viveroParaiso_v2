"""Módulo 3: gestión de usuarios con acceso al sistema (solo administrador)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from werkzeug.security import generate_password_hash

from blueprints.helpers import paginacion
from data import usuarios
from database import DatabaseError, es_restriccion_fk
from utils.auth import admin_required
from utils.validators import (
    ESTADOS_USUARIO,
    ROL_ADMIN,
    ROLES,
    clean,
    validate_choice,
    validate_email,
    validate_password,
    validate_username,
    collect_errors,
)

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _payload():
    return {
        "nombre_usuario": request.form.get("nombre_usuario", ""),
        "email": request.form.get("email", ""),
        "rol": request.form.get("rol", ""),
        "estado": request.form.get("estado", ""),
    }


def _validar(payload, contrasena, confirmacion, actual=None):
    """Valida el formulario. Con `actual` (edición) la contraseña es opcional."""
    values, errors = collect_errors(
        validate_username(payload.get("nombre_usuario")),
        validate_email(payload.get("email"), max_length=100),
        validate_choice(payload.get("rol"), ROLES, "rol"),
        validate_choice(payload.get("estado"), ESTADOS_USUARIO, "estado"),
    )
    nombre, email, rol, estado = values
    excluir_id = actual["id_usuario"] if actual else None

    if contrasena or not actual:
        _, error = validate_password(contrasena)
        if error:
            errors.append(error)
        elif contrasena != confirmacion:
            errors.append("La contraseña y su confirmación no coinciden.")

    if nombre and usuarios.nombre_existe(nombre, excluir_id):
        errors.append("Ya existe un usuario con ese nombre de usuario.")
    if email and usuarios.email_existe(email, excluir_id):
        errors.append("Ya existe un usuario con ese correo electrónico.")

    if actual and actual["rol"] == ROL_ADMIN and actual["estado"] == "Activo":
        deja_de_ser_admin = rol != ROL_ADMIN or estado != "Activo"
        if deja_de_ser_admin and actual["id_usuario"] == session.get("user_id"):
            errors.append("No puede quitarse a sí mismo el rol de administrador ni desactivar su propio usuario.")
        elif deja_de_ser_admin and usuarios.admins_activos(excluir_id=actual["id_usuario"]) == 0:
            errors.append("Debe quedar al menos un administrador activo en el sistema.")

    if errors:
        return None, errors
    return {"nombre_usuario": nombre, "email": email, "rol": rol, "estado": estado}, []


def _form(usuario, modo):
    return render_template(
        "usuarios/formulario.html", usuario=usuario, roles=ROLES, estados=ESTADOS_USUARIO, modo=modo
    )


@bp.route("/")
@admin_required
def lista():
    busqueda = clean(request.args.get("q"))
    try:
        _, total = usuarios.listar(busqueda=busqueda or None, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = usuarios.listar(busqueda=busqueda or None, limite=per_page, offset=offset)
    except DatabaseError:
        flash("No se pudieron consultar los usuarios.", "error")
        registros, total, page, pages = [], 0, 1, 1
    return render_template("usuarios/lista.html", usuarios=registros, total=total, page=page, pages=pages, q=busqueda)


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        payload = _payload()
        data, errors = _validar(payload, request.form.get("contrasena") or "", request.form.get("confirmacion") or "")
        if errors:
            for error in errors:
                flash(error, "error")
            return _form(payload, "crear")
        try:
            usuarios.create_user(
                data["nombre_usuario"],
                data["email"],
                generate_password_hash(request.form["contrasena"]),
                rol=data["rol"],
                estado=data["estado"],
            )
            flash(f"Usuario {data['nombre_usuario']} creado correctamente.", "success")
            return redirect(url_for("usuarios.lista"))
        except DatabaseError:
            flash("No se pudo crear el usuario.", "error")
            return _form(payload, "crear")
    return _form({"rol": "vendedor", "estado": "Activo"}, "crear")


@bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(usuario_id):
    actual = usuarios.obtener(usuario_id)
    if not actual:
        abort(404)
    if request.method == "POST":
        payload = _payload()
        payload["id_usuario"] = usuario_id
        contrasena = request.form.get("contrasena") or ""
        data, errors = _validar(payload, contrasena, request.form.get("confirmacion") or "", actual=actual)
        if errors:
            for error in errors:
                flash(error, "error")
            return _form(payload, "editar")
        try:
            usuarios.actualizar(usuario_id, data, generate_password_hash(contrasena) if contrasena else None)
            flash(f"Usuario {data['nombre_usuario']} actualizado correctamente.", "success")
            return redirect(url_for("usuarios.lista"))
        except DatabaseError:
            flash("No se pudo actualizar el usuario.", "error")
            return _form(payload, "editar")
    return _form(actual, "editar")


@bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(usuario_id):
    usuario = usuarios.obtener(usuario_id)
    if not usuario:
        abort(404)
    if usuario_id == session.get("user_id"):
        flash("No puede eliminar su propio usuario.", "error")
        return redirect(url_for("usuarios.lista"))
    if usuario["rol"] == ROL_ADMIN and usuario["estado"] == "Activo" and usuarios.admins_activos(excluir_id=usuario_id) == 0:
        flash("Debe quedar al menos un administrador activo en el sistema.", "error")
        return redirect(url_for("usuarios.lista"))
    movimientos = usuarios.contar_movimientos(usuario_id)
    if movimientos:
        flash(
            f"No se puede eliminar a {usuario['nombre_usuario']} porque tiene ventas o facturas registradas. "
            "Cambie su estado a Inactivo para quitarle el acceso.",
            "error",
        )
        return redirect(url_for("usuarios.lista"))
    try:
        usuarios.eliminar(usuario_id)
        flash(f"Usuario {usuario['nombre_usuario']} eliminado correctamente.", "success")
    except DatabaseError as exc:
        if es_restriccion_fk(exc):
            flash("No se puede eliminar el usuario porque tiene ventas o facturas registradas.", "error")
        else:
            flash("No se pudo eliminar el usuario.", "error")
    return redirect(url_for("usuarios.lista"))
