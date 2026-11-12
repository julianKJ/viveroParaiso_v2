from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from mysql.connector import Error

from blueprints.helpers import paginacion, form_data
from data import productos, proveedores
from database import DatabaseError, es_restriccion_fk
from utils.auth import admin_required, login_required
from utils.validators import (
    CATEGORIES,
    clean,
    required,
    validate_choice,
    validate_decimal,
    validate_int,
    collect_errors,
)

bp = Blueprint("productos", __name__, url_prefix="/productos")
FIELDS = (
    "nombre",
    "categoria",
    "descripcion",
    "precio_compra",
    "precio_venta",
    "cantidad_disponible",
    "stock_minimo",
    "id_proveedor",
)


def _validar(payload, excluir_id=None):
    values, errors = collect_errors(
        required(payload.get("nombre"), "nombre del producto"),
        validate_choice(payload.get("categoria"), CATEGORIES, "categoría"),
        (clean(payload.get("descripcion")), None),
        validate_decimal(payload.get("precio_compra"), "precio de compra"),
        validate_decimal(payload.get("precio_venta"), "precio de venta"),
        validate_int(payload.get("cantidad_disponible"), "cantidad disponible", 0),
        validate_int(payload.get("stock_minimo"), "stock mínimo", 0),
        validate_int(payload.get("id_proveedor"), "proveedor", 1),
    )
    nombre, categoria, descripcion, compra, venta, cantidad, minimo, proveedor_id = values
    if compra is not None and venta is not None and venta < compra:
        errors.append("El precio de venta no puede ser menor que el precio de compra.")
    proveedor = proveedores.obtener(proveedor_id) if proveedor_id else None
    if proveedor_id and not proveedor:
        errors.append("Seleccione un proveedor válido.")
    if proveedor and proveedor.get("estado") != "Activo" and not excluir_id:
        errors.append("El proveedor seleccionado no está activo.")
    if errors:
        return None, errors
    return {
        "nombre": nombre,
        "categoria": categoria,
        "descripcion": descripcion,
        "precio_compra": compra,
        "precio_venta": venta,
        "cantidad_disponible": cantidad,
        "stock_minimo": minimo,
        "id_proveedor": proveedor_id,
    }, []


@bp.route("/")
@login_required
def lista():
    busqueda = clean(request.args.get("q"))
    categoria = clean(request.args.get("categoria"))
    bajo_stock = request.args.get("bajo_stock") == "1"
    try:
        registros, total = productos.listar(busqueda=busqueda or None, categoria=categoria or None, bajo_stock=bajo_stock, limite=1, offset=0)
        page, per_page, offset, pages = paginacion(total)
        registros, total = productos.listar(
            busqueda=busqueda or None,
            categoria=categoria or None,
            bajo_stock=bajo_stock,
            limite=per_page,
            offset=offset,
        )
        cats = productos.categorias()
    except DatabaseError:
        flash("No se pudieron consultar los productos.", "error")
        registros, total, page, pages, cats = [], 0, 1, 1, []
    return render_template(
        "productos/lista.html",
        productos=registros,
        total=total,
        page=page,
        pages=pages,
        q=busqueda,
        categoria=categoria,
        bajo_stock=bajo_stock,
        categorias=sorted(set(list(cats) + list(CATEGORIES))),
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    lista_proveedores = proveedores.activos()
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("productos/formulario.html", producto=payload, proveedores=lista_proveedores, modo="crear")
        try:
            productos.crear(data)
            flash("Producto registrado correctamente.", "success")
            return redirect(url_for("productos.lista"))
        except DatabaseError:
            flash("No se pudo registrar el producto.", "error")
    return render_template("productos/formulario.html", producto=None, proveedores=lista_proveedores, modo="crear")


@bp.route("/<int:producto_id>")
@login_required
def detalle(producto_id):
    producto = productos.obtener(producto_id)
    if not producto:
        abort(404)
    return render_template("productos/detalle.html", producto=producto)


@bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(producto_id):
    producto = productos.obtener(producto_id)
    if not producto:
        abort(404)
    lista_proveedores = proveedores.activos()
    if producto["id_proveedor"] and not any(p["id_proveedor"] == producto["id_proveedor"] for p in lista_proveedores):
        lista_proveedores.append({"id_proveedor": producto["id_proveedor"], "nombre_empresa": producto["proveedor_nombre"]})
    if request.method == "POST":
        payload = form_data(FIELDS)
        data, errors = _validar(payload, excluir_id=producto_id)
        if errors:
            for error in errors:
                flash(error, "error")
            payload["id_producto"] = producto_id
            return render_template("productos/formulario.html", producto=payload, proveedores=lista_proveedores, modo="editar")
        try:
            productos.actualizar(producto_id, data)
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("productos.detalle", producto_id=producto_id))
        except DatabaseError:
            flash("No se pudo actualizar el producto.", "error")
    return render_template("productos/formulario.html", producto=producto, proveedores=lista_proveedores, modo="editar")


@bp.route("/<int:producto_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(producto_id):
    producto = productos.obtener(producto_id)
    if not producto:
        abort(404)
    ventas = productos.contar_ventas(producto_id)
    if ventas:
        flash(
            f"No se puede eliminar el producto porque tiene {ventas} venta(s) registrada(s). "
            "Puede dejar su stock en 0 para que no se venda más.",
            "error",
        )
        return redirect(url_for("productos.detalle", producto_id=producto_id))
    try:
        productos.eliminar(producto_id)
        flash("Producto eliminado correctamente.", "success")
    except (DatabaseError, Error) as exc:
        if es_restriccion_fk(exc):
            flash("No se puede eliminar el producto porque tiene ventas registradas.", "error")
        else:
            flash("No se pudo eliminar el producto.", "error")
    return redirect(url_for("productos.lista"))
