from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from blueprints.helpers import paginacion, form_data
from data import proveedores
from database import DatabaseError
from utils.auth import admin_required
from utils.validators import (
    ESTADOS_PROVEEDOR,
    clean,
    required,
    validate_choice,
    validate_document,
    validate_email,
    validate_phone,
    collect_errors,
)

bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")
FIELDS = (
    "nombre_empresa",
    "nit",
    "persona_contacto",
    "telefono",
    "correo",
    "direccion",
    "productos_suministrados",
    "estado",
)


def _validar(payload, excluir_id=None):
    values, errors = collect_errors(
        required(payload.get("nombre_empresa"), "nombre de la empresa"),
        validate_document(payload.get("nit")),
        required(payload.get("persona_contacto"), "persona de contacto"),
        validate_phone(payload.get("telefono")),
        validate_email(payload.get("correo")),
        required(payload.get("direccion"), "dirección"),
        (clean(payload.get("productos_suministrados")), None),
        validate_choice(payload.get("estado"), ESTADOS_PROVEEDOR, "estado"),
    )
    nombre, nit, contacto, telefono, correo, direccion, suministros, estado = values
    if nit and proveedores.nit_existe(nit, excluir_id):
        errors.append("Ya existe un proveedor con ese NIT o documento.")
    if errors:
        return None, errors
    return {
        "nombre_empresa": nombre,
        "nit": nit,
        "persona_contacto": contacto,
        "telefono": telefono,
        "correo": correo,
        "direccion": direccion,
        "productos_suministrados": suministros,
        "estado": estado,
    }, []


@bp.route("/")
@admin_required
def lista():
    busqueda = clean(request.args.get("q"))
    try:
        _, total = proveedores.listar(busqueda=busqueda or None, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = proveedores.listar(busqueda=busqueda or None, limite=per_page, offset=offset)
    except DatabaseError:
        flash("No se pudieron consultar los proveedores.", "error")
        registros, total, page, pages = [], 0, 1, 1
    return render_template(
        "proveedores/lista.html",
        proveedores=registros,
        total=total,
        page=page,
        pages=pages,
        q=busqueda,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("proveedores/formulario.html", proveedor=payload, modo="crear")
        try:
            proveedores.crear(data)
            flash("Proveedor registrado correctamente.", "success")
            return redirect(url_for("proveedores.lista"))
        except DatabaseError:
            flash("No se pudo registrar el proveedor.", "error")
    return render_template("proveedores/formulario.html", proveedor=None, modo="crear")


@bp.route("/<int:proveedor_id>")
@admin_required
def detalle(proveedor_id):
    proveedor = proveedores.obtener(proveedor_id)
    if not proveedor:
        abort(404)
    asociados = proveedores.contar_productos(proveedor_id)
    return render_template("proveedores/detalle.html", proveedor=proveedor, asociados=asociados)


@bp.route("/<int:proveedor_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(proveedor_id):
    proveedor = proveedores.obtener(proveedor_id)
    if not proveedor:
        abort(404)
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload, excluir_id=proveedor_id)
        if errors:
            for error in errors:
                flash(error, "error")
            payload["id_proveedor"] = proveedor_id
            return render_template("proveedores/formulario.html", proveedor=payload, modo="editar")
        try:
            proveedores.actualizar(proveedor_id, data)
            flash("Proveedor actualizado correctamente.", "success")
            return redirect(url_for("proveedores.detalle", proveedor_id=proveedor_id))
        except DatabaseError:
            flash("No se pudo actualizar el proveedor.", "error")
    return render_template("proveedores/formulario.html", proveedor=proveedor, modo="editar")


@bp.route("/<int:proveedor_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(proveedor_id):
    proveedor = proveedores.obtener(proveedor_id)
    if not proveedor:
        abort(404)
    asociados = proveedores.contar_productos(proveedor_id)
    if asociados:
        flash(
            f"No se puede eliminar el proveedor porque tiene {asociados} producto(s) asociado(s). "
            "Reasigne o elimine esos productos antes de continuar.",
            "error",
        )
        return redirect(url_for("proveedores.detalle", proveedor_id=proveedor_id))
    try:
        proveedores.eliminar(proveedor_id)
        flash("Proveedor eliminado correctamente.", "success")
    except DatabaseError:
        flash(
            "No se pudo eliminar el proveedor. Si tiene productos asociados, resuelva esa relación primero.",
            "error",
        )
    return redirect(url_for("proveedores.lista"))
