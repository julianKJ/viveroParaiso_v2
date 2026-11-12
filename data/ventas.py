"""Módulo 2: registro de ventas. Cada venta descuenta su cantidad de la tabla stock."""
from decimal import Decimal

from database import query_all, query_one, transaction


class VentaError(Exception):
    """Regla de negocio que impide registrar la venta (por ejemplo, stock insuficiente)."""


SELECT_VENTA = """
    SELECT v.id_venta, v.id_cliente, v.id_producto, v.id_usuario, v.cantidad,
           v.precio_unitario, v.total, v.fecha_venta,
           c.nombre AS cliente_nombre, c.email AS cliente_email, c.ciudad AS cliente_ciudad,
           c.pais AS cliente_pais,
           p.nombre AS producto_nombre, p.categoria AS producto_categoria,
           u.nombre_usuario AS vendedor,
           f.id_factura, f.numero_factura
    FROM venta v
    INNER JOIN cliente c ON c.id_cliente = v.id_cliente
    INNER JOIN producto p ON p.id_producto = v.id_producto
    INNER JOIN usuarios u ON u.id_usuario = v.id_usuario
    LEFT JOIN historial_facturas f ON f.id_venta = v.id_venta
"""


def registrar(id_cliente, id_producto, cantidad, id_usuario):
    """Registra la venta y descuenta el stock en una sola transacción.

    Bloquea la fila de stock del producto (FOR UPDATE) para que dos ventas
    simultáneas no vendan las mismas unidades.
    """
    with transaction() as cur:
        cur.execute("SELECT id_cliente FROM cliente WHERE id_cliente = %s", (id_cliente,))
        if not cur.fetchone():
            raise VentaError("El cliente seleccionado no existe.")

        cur.execute(
            """
            SELECT p.precio_venta, p.nombre, s.cantidad_disponible
            FROM producto p
            INNER JOIN stock s ON s.id_producto = p.id_producto
            WHERE p.id_producto = %s
            FOR UPDATE
            """,
            (id_producto,),
        )
        producto = cur.fetchone()
        if not producto:
            raise VentaError("El producto seleccionado no existe o no tiene stock registrado.")
        disponible = int(producto["cantidad_disponible"])
        if cantidad > disponible:
            raise VentaError(
                f"Stock insuficiente de {producto['nombre']}: solo quedan {disponible} unidad(es)."
            )

        precio = Decimal(producto["precio_venta"])
        total = precio * cantidad
        cur.execute(
            """
            UPDATE stock
            SET cantidad_disponible = cantidad_disponible - %s
            WHERE id_producto = %s AND cantidad_disponible >= %s
            """,
            (cantidad, id_producto, cantidad),
        )
        if cur.rowcount != 1:
            raise VentaError("El stock cambió mientras se registraba la venta. Inténtelo de nuevo.")

        cur.execute(
            """
            INSERT INTO venta (id_cliente, id_producto, id_usuario, cantidad, precio_unitario, total)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id_cliente, id_producto, id_usuario, cantidad, precio, total),
        )
        return cur.lastrowid


def listar(busqueda=None, limite=10, offset=0):
    where = ""
    params = []
    if busqueda:
        where = """
            WHERE c.nombre LIKE %s
               OR p.nombre LIKE %s
               OR u.nombre_usuario LIKE %s
               OR f.numero_factura LIKE %s
        """
        term = f"%{busqueda}%"
        params.extend([term, term, term, term])
    total_row = query_one(
        f"""
        SELECT COUNT(*) AS total
        FROM venta v
        INNER JOIN cliente c ON c.id_cliente = v.id_cliente
        INNER JOIN producto p ON p.id_producto = v.id_producto
        INNER JOIN usuarios u ON u.id_usuario = v.id_usuario
        LEFT JOIN historial_facturas f ON f.id_venta = v.id_venta
        {where}
        """,
        tuple(params),
    )
    sql = f"""
        {SELECT_VENTA}
        {where}
        ORDER BY v.fecha_venta DESC, v.id_venta DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limite, offset])
    return query_all(sql, tuple(params)), int(total_row["total"]) if total_row else 0


def obtener(id_venta):
    return query_one(f"{SELECT_VENTA} WHERE v.id_venta = %s", (id_venta,))


def recientes(limite=5):
    return query_all(f"{SELECT_VENTA} ORDER BY v.fecha_venta DESC, v.id_venta DESC LIMIT %s", (limite,))


def resumen_hoy():
    row = query_one(
        """
        SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS ingresos
        FROM venta
        WHERE DATE(fecha_venta) = CURDATE()
        """
    )
    return {
        "cantidad": int(row["cantidad"]) if row else 0,
        "ingresos": row["ingresos"] if row else 0,
    }
