from database import query_all, query_one, execute, transaction

# Producto con sus existencias (tabla stock) y el nombre del proveedor.
SELECT_PRODUCTO = """
    SELECT p.id_producto, p.nombre, p.categoria, p.descripcion, p.precio_compra, p.precio_venta,
           p.id_proveedor, p.fecha_registro,
           COALESCE(s.cantidad_disponible, 0) AS cantidad_disponible,
           COALESCE(s.stock_minimo, 0) AS stock_minimo,
           s.fecha_actualizacion,
           pr.nombre_empresa AS proveedor_nombre
    FROM producto p
    INNER JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
    LEFT JOIN stock s ON s.id_producto = p.id_producto
"""


def _filtros(busqueda=None, categoria=None, bajo_stock=False):
    clauses = []
    params = []
    if busqueda:
        clauses.append("(p.nombre LIKE %s OR p.categoria LIKE %s OR p.descripcion LIKE %s)")
        term = f"%{busqueda}%"
        params.extend([term, term, term])
    if categoria:
        clauses.append("p.categoria = %s")
        params.append(categoria)
    if bajo_stock:
        clauses.append("COALESCE(s.cantidad_disponible, 0) <= COALESCE(s.stock_minimo, 0)")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def listar(busqueda=None, categoria=None, bajo_stock=False, limite=10, offset=0):
    where, params = _filtros(busqueda, categoria, bajo_stock)
    total_row = query_one(
        f"SELECT COUNT(*) AS total FROM producto p LEFT JOIN stock s ON s.id_producto = p.id_producto {where}",
        tuple(params),
    )
    sql = f"""
        {SELECT_PRODUCTO}
        {where}
        ORDER BY p.fecha_registro DESC, p.id_producto DESC
        LIMIT %s OFFSET %s
    """
    query_params = list(params)
    query_params.extend([limite, offset])
    return query_all(sql, tuple(query_params)), int(total_row["total"]) if total_row else 0


def obtener(id_producto):
    return query_one(f"{SELECT_PRODUCTO} WHERE p.id_producto = %s", (id_producto,))


def disponibles_para_venta():
    """Productos con existencias, para el formulario de venta."""
    return query_all(
        f"""
        {SELECT_PRODUCTO}
        WHERE COALESCE(s.cantidad_disponible, 0) > 0
        ORDER BY p.nombre
        """
    )


def crear(data):
    """Inserta el producto y su fila de stock en una sola transacción."""
    with transaction() as cur:
        cur.execute(
            """
            INSERT INTO producto
                (nombre, categoria, descripcion, precio_compra, precio_venta, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data["nombre"],
                data["categoria"],
                data.get("descripcion") or None,
                data["precio_compra"],
                data["precio_venta"],
                data["id_proveedor"],
            ),
        )
        id_producto = cur.lastrowid
        cur.execute(
            "INSERT INTO stock (id_producto, cantidad_disponible, stock_minimo) VALUES (%s, %s, %s)",
            (id_producto, data["cantidad_disponible"], data["stock_minimo"]),
        )
    return id_producto


def actualizar(id_producto, data):
    with transaction() as cur:
        cur.execute(
            """
            UPDATE producto
            SET nombre = %s, categoria = %s, descripcion = %s, precio_compra = %s,
                precio_venta = %s, id_proveedor = %s
            WHERE id_producto = %s
            """,
            (
                data["nombre"],
                data["categoria"],
                data.get("descripcion") or None,
                data["precio_compra"],
                data["precio_venta"],
                data["id_proveedor"],
                id_producto,
            ),
        )
        count = cur.rowcount
        # Crea la fila de stock si faltara, o la actualiza si ya existe
        cur.execute(
            """
            INSERT INTO stock (id_producto, cantidad_disponible, stock_minimo)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                cantidad_disponible = VALUES(cantidad_disponible),
                stock_minimo = VALUES(stock_minimo)
            """,
            (id_producto, data["cantidad_disponible"], data["stock_minimo"]),
        )
    return count


def contar_ventas(id_producto):
    row = query_one("SELECT COUNT(*) AS total FROM venta WHERE id_producto = %s", (id_producto,))
    return int(row["total"]) if row else 0


def eliminar(id_producto):
    # La fila de stock se borra sola (ON DELETE CASCADE)
    _, count = execute("DELETE FROM producto WHERE id_producto = %s", (id_producto,))
    return count


def total():
    row = query_one("SELECT COUNT(*) AS total FROM producto")
    return int(row["total"]) if row else 0


def recientes(limite=5):
    return query_all(
        f"""
        {SELECT_PRODUCTO}
        ORDER BY p.fecha_registro DESC, p.id_producto DESC
        LIMIT %s
        """,
        (limite,),
    )


def stock_bajo(limite=8):
    return query_all(
        f"""
        {SELECT_PRODUCTO}
        WHERE COALESCE(s.cantidad_disponible, 0) <= COALESCE(s.stock_minimo, 0)
        ORDER BY cantidad_disponible ASC
        LIMIT %s
        """,
        (limite,),
    )


def categorias():
    rows = query_all("SELECT DISTINCT categoria FROM producto ORDER BY categoria")
    return [row["categoria"] for row in rows]
