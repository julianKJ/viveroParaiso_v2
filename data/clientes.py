from database import query_all, query_one, execute

COLUMNAS = "id_cliente, nombre, email, telefono, direccion, ciudad, pais, fecha_registro"


def listar(busqueda=None, limite=10, offset=0):
    where = ""
    params = []
    if busqueda:
        where = """
            WHERE nombre LIKE %s
               OR email LIKE %s
               OR ciudad LIKE %s
               OR pais LIKE %s
        """
        term = f"%{busqueda}%"
        params.extend([term, term, term, term])
    total_row = query_one(f"SELECT COUNT(*) AS total FROM cliente {where}", tuple(params))
    sql = f"""
        SELECT {COLUMNAS}
        FROM cliente
        {where}
        ORDER BY nombre ASC
        LIMIT %s OFFSET %s
    """
    params.extend([limite, offset])
    return query_all(sql, tuple(params)), int(total_row["total"]) if total_row else 0


def todos():
    """Lista completa para elegir el cliente de una venta."""
    return query_all("SELECT id_cliente, nombre, email, ciudad, pais FROM cliente ORDER BY nombre")


def obtener(id_cliente):
    return query_one(f"SELECT {COLUMNAS} FROM cliente WHERE id_cliente = %s", (id_cliente,))


def email_existe(email, excluir_id=None):
    row = query_one(
        "SELECT id_cliente FROM cliente WHERE email = %s AND id_cliente <> %s",
        (email, excluir_id or 0),
    )
    return row is not None


def crear(data):
    sql = """
        INSERT INTO cliente (nombre, email, telefono, direccion, ciudad, pais)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    last_id, _ = execute(
        sql,
        (data["nombre"], data["email"], data["telefono"], data["direccion"], data["ciudad"], data["pais"]),
    )
    return last_id


def actualizar(id_cliente, data):
    sql = """
        UPDATE cliente
        SET nombre = %s, email = %s, telefono = %s, direccion = %s, ciudad = %s, pais = %s
        WHERE id_cliente = %s
    """
    _, count = execute(
        sql,
        (
            data["nombre"],
            data["email"],
            data["telefono"],
            data["direccion"],
            data["ciudad"],
            data["pais"],
            id_cliente,
        ),
    )
    return count


def contar_ventas(id_cliente):
    row = query_one("SELECT COUNT(*) AS total FROM venta WHERE id_cliente = %s", (id_cliente,))
    return int(row["total"]) if row else 0


def eliminar(id_cliente):
    _, count = execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
    return count


def total():
    row = query_one("SELECT COUNT(*) AS total FROM cliente")
    return int(row["total"]) if row else 0


def reporte_por_pais():
    """Opción B: clientes agrupados por nacionalidad (país), con el total de cada grupo."""
    filas = query_all(f"SELECT {COLUMNAS} FROM cliente ORDER BY pais ASC, nombre ASC")
    grupos = []
    for fila in filas:
        if not grupos or grupos[-1]["pais"] != fila["pais"]:
            grupos.append({"pais": fila["pais"], "clientes": []})
        grupos[-1]["clientes"].append(fila)
    for grupo in grupos:
        grupo["total"] = len(grupo["clientes"])
        grupo["porcentaje"] = round(grupo["total"] * 100 / len(filas), 1)
    grupos.sort(key=lambda g: (-g["total"], g["pais"]))
    return grupos, len(filas)
