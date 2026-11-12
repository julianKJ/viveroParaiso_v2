from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from blueprints.helpers import paginacion, form_data
from data import empleados
from database import DatabaseError
from utils.auth import admin_required
from utils.validators import (
    CARGOS,
    DOCUMENT_TYPES,
    ESTADOS_LABORALES,
    clean,
    required,
    validate_choice,
    validate_date,
    validate_document,
    validate_email,
    validate_phone,
    collect_errors,
)

bp = Blueprint("empleados", __name__, url_prefix="/empleados")
FIELDS = (
    "nombres",
    "apellidos",
    "tipo_documento",
    "numero_documento",
    "cargo",
    "telefono",
    "correo",
    "fecha_contratacion",
    "estado_laboral",
)


def _validar(payload, excluir_id=None):
    values, errors = collect_errors(
        required(payload.get("nombres"), "nombres"),
        required(payload.get("apellidos"), "apellidos"),
        validate_choice(payload.get("tipo_documento"), DOCUMENT_TYPES, "tipo de documento"),
        validate_document(payload.get("numero_documento")),
        validate_choice(payload.get("cargo"), CARGOS, "cargo"),
        validate_phone(payload.get("telefono")),
        validate_email(payload.get("correo")),
        validate_date(payload.get("fecha_contratacion"), "fecha de contratación"),
        validate_choice(payload.get("estado_laboral"), ESTADOS_LABORALES, "estado laboral"),
    )
    nombres, apellidos, tipo, numero, cargo, telefono, correo, fecha, estado = values
    if numero and empleados.documento_existe(numero, excluir_id):
        errors.append("Ya existe un empleado con ese número de documento.")
    if correo and empleados.correo_existe(correo, excluir_id):
        errors.append("Ya existe un empleado con ese correo electrónico.")
    if errors:
        return None, errors
    return {
        "nombres": nombres,
        "apellidos": apellidos,
        "tipo_documento": tipo,
        "numero_documento": numero,
        "cargo": cargo,
        "telefono": telefono,
        "correo": correo,
        "fecha_contratacion": fecha,
        "estado_laboral": estado,
    }, []


@bp.route("/")
@admin_required
def lista():
    busqueda = clean(request.args.get("q"))
    try:
        _, total = empleados.listar(busqueda=busqueda or None, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = empleados.listar(busqueda=busqueda or None, limite=per_page, offset=offset)
    except DatabaseError:
        flash("No se pudieron consultar los empleados.", "error")
        registros, total, page, pages = [], 0, 1, 1
    return render_template("empleados/lista.html", empleados=registros, total=total, page=page, pages=pages, q=busqueda)


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("empleados/formulario.html", empleado=payload, modo="crear")
        try:
            empleados.crear(data)
            flash("Empleado registrado correctamente.", "success")
            return redirect(url_for("empleados.lista"))
        except DatabaseError:
            flash("No se pudo registrar el empleado.", "error")
    return render_template("empleados/formulario.html", empleado=None, modo="crear")


@bp.route("/<int:empleado_id>")
@admin_required
def detalle(empleado_id):
    empleado = empleados.obtener(empleado_id)
    if not empleado:
        abort(404)
    return render_template("empleados/detalle.html", empleado=empleado)


@bp.route("/<int:empleado_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(empleado_id):
    empleado = empleados.obtener(empleado_id)
    if not empleado:
        abort(404)
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload, excluir_id=empleado_id)
        if errors:
            for error in errors:
                flash(error, "error")
            payload["id_empleado"] = empleado_id
            return render_template("empleados/formulario.html", empleado=payload, modo="editar")
        try:
            empleados.actualizar(empleado_id, data)
            flash("Empleado actualizado correctamente.", "success")
            return redirect(url_for("empleados.detalle", empleado_id=empleado_id))
        except DatabaseError:
            flash("No se pudo actualizar el empleado.", "error")
    return render_template("empleados/formulario.html", empleado=empleado, modo="editar")


@bp.route("/<int:empleado_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(empleado_id):
    empleado = empleados.obtener(empleado_id)
    if not empleado:
        abort(404)
    try:
        empleados.eliminar(empleado_id)
        flash("Empleado eliminado correctamente.", "success")
    except DatabaseError:
        flash("No se pudo eliminar el empleado.", "error")
    return redirect(url_for("empleados.lista"))
