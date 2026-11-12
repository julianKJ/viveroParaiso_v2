"""Módulo 2: registro de ventas y facturas (administrador y vendedor)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session

from blueprints.helpers import paginacion
from data import clientes, facturas, productos, ventas
from data.ventas import VentaError
from database import DatabaseError
from utils.auth import login_required
from utils.validators import clean, validate_int, collect_errors

bp = Blueprint("ventas", __name__, url_prefix="/ventas")


def _opciones():
    return clientes.todos(), productos.disponibles_para_venta()


@bp.route("/")
@login_required
def lista():
    busqueda = clean(request.args.get("q"))
    try:
        _, total = ventas.listar(busqueda=busqueda or None, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = ventas.listar(busqueda=busqueda or None, limite=per_page, offset=offset)
        hoy = ventas.resumen_hoy()
    except DatabaseError:
        flash("No se pudieron consultar las ventas.", "error")
        registros, total, page, pages, hoy = [], 0, 1, 1, {"cantidad": 0, "ingresos": 0}
    return render_template(
        "ventas/lista.html", ventas=registros, total=total, page=page, pages=pages, q=busqueda, hoy=hoy
    )


@bp.route("/nueva", methods=["GET", "POST"])
@login_required
def crear():
    lista_clientes, lista_productos = _opciones()
    seleccion = {
        "id_cliente": request.args.get("cliente", ""),
        "id_producto": request.args.get("producto", ""),
        "cantidad": "1",
        "generar_factura": True,
    }
    if request.method == "POST":
        seleccion = {
            "id_cliente": request.form.get("id_cliente", ""),
            "id_producto": request.form.get("id_producto", ""),
            "cantidad": request.form.get("cantidad", ""),
            "generar_factura": request.form.get("generar_factura") == "1",
        }
        (id_cliente, id_producto, cantidad), errors = collect_errors(
            validate_int(seleccion["id_cliente"], "cliente", 1),
            validate_int(seleccion["id_producto"], "producto", 1),
            validate_int(seleccion["cantidad"], "cantidad", 1),
        )
        if not errors:
            try:
                id_venta = ventas.registrar(id_cliente, id_producto, cantidad, session["user_id"])
            except VentaError as exc:
                errors.append(str(exc))
            except DatabaseError:
                errors.append("No se pudo registrar la venta. Inténtelo de nuevo.")
            else:
                flash("Venta registrada y stock actualizado.", "success")
                if seleccion["generar_factura"]:
                    try:
                        id_factura, _ = facturas.generar(id_venta, session["user_id"])
                        flash("Factura generada y guardada en el historial.", "success")
                        return redirect(url_for("ventas.factura", factura_id=id_factura))
                    except (VentaError, DatabaseError):
                        flash("La venta quedó registrada, pero no se pudo generar la factura. Genérela desde el detalle.", "warning")
                return redirect(url_for("ventas.detalle", venta_id=id_venta))
        for error in errors:
            flash(error, "error")
        lista_clientes, lista_productos = _opciones()
    return render_template(
        "ventas/formulario.html", clientes=lista_clientes, productos=lista_productos, seleccion=seleccion
    )


@bp.route("/<int:venta_id>")
@login_required
def detalle(venta_id):
    venta = ventas.obtener(venta_id)
    if not venta:
        abort(404)
    return render_template("ventas/detalle.html", venta=venta)


@bp.route("/<int:venta_id>/factura", methods=["POST"])
@login_required
def generar_factura(venta_id):
    if not ventas.obtener(venta_id):
        abort(404)
    try:
        id_factura, nueva = facturas.generar(venta_id, session["user_id"])
    except (VentaError, DatabaseError):
        flash("No se pudo generar la factura.", "error")
        return redirect(url_for("ventas.detalle", venta_id=venta_id))
    if nueva:
        flash("Factura generada y guardada en el historial.", "success")
    else:
        flash("Esta venta ya tenía factura; se muestra la existente.", "warning")
    return redirect(url_for("ventas.factura", factura_id=id_factura))


@bp.route("/facturas")
@login_required
def facturas_lista():
    busqueda = clean(request.args.get("q"))
    try:
        _, total = facturas.listar(busqueda=busqueda or None, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = facturas.listar(busqueda=busqueda or None, limite=per_page, offset=offset)
    except DatabaseError:
        flash("No se pudo consultar el historial de facturas.", "error")
        registros, total, page, pages = [], 0, 1, 1
    return render_template(
        "ventas/facturas.html", facturas=registros, total=total, page=page, pages=pages, q=busqueda
    )


@bp.route("/facturas/<int:factura_id>")
@login_required
def factura(factura_id):
    registro = facturas.obtener(factura_id)
    if not registro:
        abort(404)
    return render_template("ventas/factura.html", factura=registro)
