from database import query_all, query_one, execute


def listar(busqueda=None, limite=10, offset=0):
    where = ""
    params = []
    if busqueda:
        where = """
            WHERE nombre_empresa LIKE %s
               OR nit LIKE %s
               OR persona_contacto LIKE %s
               OR correo LIKE %s
        """
        term = f"%{busqueda}%"
        params.extend([term, term, term, term])
    total_row = query_one(f"SELECT COUNT(*) AS total FROM proveedor {where}", tuple(params))
    sql = f"""
        SELECT id_proveedor, nombre_empresa, nit, persona_contacto, telefono, correo,
               direccion, productos_suministrados, estado, fecha_registro
        FROM proveedor
        {where}
        ORDER BY nombre_empresa ASC
        LIMIT %s OFFSET %s
    """
    params.extend([limite, offset])
    return query_all(sql, tuple(params)), int(total_row["total"]) if total_row else 0


def obtener(proveedor_id):
    return query_one("SELECT * FROM proveedor WHERE id_proveedor = %s", (proveedor_id,))


def activos():
    return query_all(
        "SELECT id_proveedor, nombre_empresa FROM proveedor WHERE estado = 'Activo' ORDER BY nombre_empresa"
    )


def nit_existe(nit, excluir_id=None):
    if excluir_id:
        row = query_one(
            "SELECT id_proveedor FROM proveedor WHERE nit = %s AND id_proveedor <> %s",
            (nit, excluir_id),
        )
    else:
        row = query_one("SELECT id_proveedor FROM proveedor WHERE nit = %s", (nit,))
    return row is not None


def crear(data):
    sql = """
        INSERT INTO proveedor
            (nombre_empresa, nit, persona_contacto, telefono, correo, direccion, productos_suministrados, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    last_id, _ = execute(
        sql,
        (
            data["nombre_empresa"],
            data["nit"],
            data["persona_contacto"],
            data["telefono"],
            data["correo"],
            data["direccion"],
            data.get("productos_suministrados") or None,
            data["estado"],
        ),
    )
    return last_id


def actualizar(proveedor_id, data):
    sql = """
        UPDATE proveedor
        SET nombre_empresa = %s, nit = %s, persona_contacto = %s, telefono = %s,
            correo = %s, direccion = %s, productos_suministrados = %s, estado = %s
        WHERE id_proveedor = %s
    """
    _, count = execute(
        sql,
        (
            data["nombre_empresa"],
            data["nit"],
            data["persona_contacto"],
            data["telefono"],
            data["correo"],
            data["direccion"],
            data.get("productos_suministrados") or None,
            data["estado"],
            proveedor_id,
        ),
    )
    return count


def contar_productos(proveedor_id):
    row = query_one(
        "SELECT COUNT(*) AS total FROM producto WHERE id_proveedor = %s",
        (proveedor_id,),
    )
    return int(row["total"]) if row else 0


def eliminar(proveedor_id):
    _, count = execute("DELETE FROM proveedor WHERE id_proveedor = %s", (proveedor_id,))
    return count


def total():
    row = query_one("SELECT COUNT(*) AS total FROM proveedor")
    return int(row["total"]) if row else 0
