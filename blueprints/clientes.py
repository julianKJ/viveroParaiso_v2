"""Módulo 1: gestión de clientes (administrador y vendedor)."""
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from blueprints.helpers import paginacion, form_data
from data import clientes
from database import DatabaseError, es_restriccion_fk
from utils.auth import login_required
from utils.validators import (
    PAISES,
    clean,
    validate_choice,
    validate_email,
    validate_phone,
    validate_text,
    collect_errors,
)

bp = Blueprint("clientes", __name__, url_prefix="/clientes")
FIELDS = ("nombre", "email", "telefono", "direccion", "ciudad", "pais")


def _validar(payload, excluir_id=None):
    values, errors = collect_errors(
        validate_text(payload.get("nombre"), "nombre completo", 100),
        validate_email(payload.get("email"), max_length=100),
        validate_phone(payload.get("telefono")),
        validate_text(payload.get("direccion"), "dirección", 150),
        validate_text(payload.get("ciudad"), "ciudad", 50),
        validate_choice(payload.get("pais"), PAISES, "país"),
    )
    nombre, email, telefono, direccion, ciudad, pais = values
    if email and clientes.email_existe(email, excluir_id):
        errors.append("Ya existe un cliente con ese correo electrónico.")
    if errors:
        return None, errors
    return {
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "direccion": direccion,
        "ciudad": ciudad,
        "pais": pais,
    }, []


@bp.route("/")
@login_required
def lista():
    busqueda = clean(request.args.get("q"))
    try:
        _, total = clientes.listar(busqueda=busqueda or None, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = clientes.listar(busqueda=busqueda or None, limite=per_page, offset=offset)
    except DatabaseError:
        flash("No se pudieron consultar los clientes.", "error")
        registros, total, page, pages = [], 0, 1, 1
    return render_template("clientes/lista.html", clientes=registros, total=total, page=page, pages=pages, q=busqueda)


@bp.route("/reporte")
@login_required
def reporte():
    """Opción B: todos los clientes en pantalla y reporte imprimible por nacionalidad."""
    try:
        grupos, total = clientes.reporte_por_pais()
    except DatabaseError:
        flash("No se pudo generar el reporte de clientes.", "error")
        grupos, total = [], 0
    return render_template("clientes/reporte.html", grupos=grupos, total=total, generado=datetime.now())


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("clientes/formulario.html", cliente=payload, paises=PAISES, modo="crear")
        try:
            clientes.crear(data)
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for("clientes.lista"))
        except DatabaseError:
            flash("No se pudo registrar el cliente.", "error")
    return render_template("clientes/formulario.html", cliente=None, paises=PAISES, modo="crear")


@bp.route("/<int:cliente_id>")
@login_required
def detalle(cliente_id):
    cliente = clientes.obtener(cliente_id)
    if not cliente:
        abort(404)
    return render_template("clientes/detalle.html", cliente=cliente, ventas=clientes.contar_ventas(cliente_id))


@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@login_required
def editar(cliente_id):
    cliente = clientes.obtener(cliente_id)
    if not cliente:
        abort(404)
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload, excluir_id=cliente_id)
        if errors:
            for error in errors:
                flash(error, "error")
            payload["id_cliente"] = cliente_id
            return render_template("clientes/formulario.html", cliente=payload, paises=PAISES, modo="editar")
        try:
            clientes.actualizar(cliente_id, data)
            flash("Cliente actualizado correctamente.", "success")
            return redirect(url_for("clientes.detalle", cliente_id=cliente_id))
        except DatabaseError:
            flash("No se pudo actualizar el cliente.", "error")
    return render_template("clientes/formulario.html", cliente=cliente, paises=PAISES, modo="editar")


@bp.route("/<int:cliente_id>/eliminar", methods=["POST"])
@login_required
def eliminar(cliente_id):
    cliente = clientes.obtener(cliente_id)
    if not cliente:
        abort(404)
    ventas = clientes.contar_ventas(cliente_id)
    if ventas:
        flash(
            f"No se puede eliminar al cliente porque tiene {ventas} venta(s) registrada(s).",
            "error",
        )
        return redirect(url_for("clientes.detalle", cliente_id=cliente_id))
    try:
        clientes.eliminar(cliente_id)
        flash("Cliente eliminado correctamente.", "success")
    except DatabaseError as exc:
        if es_restriccion_fk(exc):
            flash("No se puede eliminar al cliente porque tiene ventas registradas.", "error")
        else:
            flash("No se pudo eliminar el cliente.", "error")
    return redirect(url_for("clientes.lista"))
