"""Módulo 2: facturas de venta guardadas en la tabla historial_facturas."""
from database import query_all, query_one, transaction
from data.ventas import VentaError

SELECT_FACTURA = """
    SELECT f.id_factura, f.numero_factura, f.id_venta, f.id_usuario, f.cliente_nombre,
           f.cliente_email, f.cliente_direccion, f.cliente_ciudad, f.cliente_pais,
           f.producto_nombre, f.cantidad, f.precio_unitario, f.total, f.fecha_emision,
           v.fecha_venta, v.id_cliente, v.id_producto,
           u.nombre_usuario AS generada_por,
           uv.nombre_usuario AS vendedor
    FROM historial_facturas f
    INNER JOIN venta v ON v.id_venta = f.id_venta
    INNER JOIN usuarios u ON u.id_usuario = f.id_usuario
    INNER JOIN usuarios uv ON uv.id_usuario = v.id_usuario
"""


def numero_para(id_venta):
    return f"FV-{id_venta:06d}"


def generar(id_venta, id_usuario):
    """Crea la factura de una venta y la guarda en el historial.

    Si la venta ya tiene factura, devuelve esa misma: una venta nunca
    tiene dos facturas.
    """
    with transaction() as cur:
        cur.execute(
            """
            SELECT v.id_venta, v.cantidad, v.precio_unitario, v.total,
                   c.nombre, c.email, c.direccion, c.ciudad, c.pais,
                   p.nombre AS producto
            FROM venta v
            INNER JOIN cliente c ON c.id_cliente = v.id_cliente
            INNER JOIN producto p ON p.id_producto = v.id_producto
            WHERE v.id_venta = %s
            FOR UPDATE
            """,
            (id_venta,),
        )
        venta = cur.fetchone()
        if not venta:
            raise VentaError("La venta no existe.")

        cur.execute("SELECT id_factura FROM historial_facturas WHERE id_venta = %s", (id_venta,))
        existente = cur.fetchone()
        if existente:
            return existente["id_factura"], False

        cur.execute(
            """
            INSERT INTO historial_facturas
                (numero_factura, id_venta, id_usuario, cliente_nombre, cliente_email,
                 cliente_direccion, cliente_ciudad, cliente_pais, producto_nombre,
                 cantidad, precio_unitario, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                numero_para(id_venta),
                id_venta,
                id_usuario,
                venta["nombre"],
                venta["email"],
                venta["direccion"],
                venta["ciudad"],
                venta["pais"],
                venta["producto"],
                venta["cantidad"],
                venta["precio_unitario"],
                venta["total"],
            ),
        )
        return cur.lastrowid, True


def listar(busqueda=None, limite=10, offset=0):
    where = ""
    params = []
    if busqueda:
        where = """
            WHERE f.numero_factura LIKE %s
               OR f.cliente_nombre LIKE %s
               OR f.producto_nombre LIKE %s
        """
        term = f"%{busqueda}%"
        params.extend([term, term, term])
    total_row = query_one(f"SELECT COUNT(*) AS total FROM historial_facturas f {where}", tuple(params))
    sql = f"""
        {SELECT_FACTURA}
        {where}
        ORDER BY f.fecha_emision DESC, f.id_factura DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limite, offset])
    return query_all(sql, tuple(params)), int(total_row["total"]) if total_row else 0


def obtener(id_factura):
    return query_one(f"{SELECT_FACTURA} WHERE f.id_factura = %s", (id_factura,))


def total():
    row = query_one("SELECT COUNT(*) AS total FROM historial_facturas")
    return int(row["total"]) if row else 0
