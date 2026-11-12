from datetime import datetime, timedelta
from database import query_all, query_one, execute

from utils.validators import ROL_ADMIN

COLUMNAS = "id_usuario, nombre_usuario, email, rol, estado"


# ---------- Inicio de sesión (módulo 0) ----------

def find_by_login(identificador):
    sql = """
        SELECT id_usuario, nombre_usuario, email, contrasena, rol, estado
        FROM usuarios
        WHERE nombre_usuario = %s OR email = %s
        LIMIT 1
    """
    return query_one(sql, (identificador, identificador))


def find_by_username(nombre_usuario):
    return query_one("SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s LIMIT 1", (nombre_usuario,))


def find_by_email(email):
    return query_one("SELECT id_usuario FROM usuarios WHERE email = %s LIMIT 1", (email,))


# ---------- CRUD de usuarios (módulo 3) ----------

def listar(busqueda=None, limite=10, offset=0):
    where = ""
    params = []
    if busqueda:
        where = "WHERE nombre_usuario LIKE %s OR email LIKE %s OR rol LIKE %s"
        term = f"%{busqueda}%"
        params.extend([term, term, term])
    total_row = query_one(f"SELECT COUNT(*) AS total FROM usuarios {where}", tuple(params))
    sql = f"""
        SELECT {COLUMNAS}
        FROM usuarios
        {where}
        ORDER BY rol ASC, nombre_usuario ASC
        LIMIT %s OFFSET %s
    """
    params.extend([limite, offset])
    return query_all(sql, tuple(params)), int(total_row["total"]) if total_row else 0


def obtener(id_usuario):
    return query_one(f"SELECT {COLUMNAS} FROM usuarios WHERE id_usuario = %s", (id_usuario,))


def nombre_existe(nombre_usuario, excluir_id=None):
    row = query_one(
        "SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s AND id_usuario <> %s",
        (nombre_usuario, excluir_id or 0),
    )
    return row is not None


def email_existe(email, excluir_id=None):
    row = query_one(
        "SELECT id_usuario FROM usuarios WHERE email = %s AND id_usuario <> %s",
        (email, excluir_id or 0),
    )
    return row is not None


def create_user(nombre_usuario, email, contrasena_hash, rol=ROL_ADMIN, estado="Activo"):
    sql = """
        INSERT INTO usuarios (nombre_usuario, email, contrasena, rol, estado)
        VALUES (%s, %s, %s, %s, %s)
    """
    last_id, _ = execute(sql, (nombre_usuario, email, contrasena_hash, rol, estado))
    return last_id


def actualizar(id_usuario, data, contrasena_hash=None):
    campos = "nombre_usuario = %s, email = %s, rol = %s, estado = %s"
    params = [data["nombre_usuario"], data["email"], data["rol"], data["estado"]]
    if contrasena_hash:
        campos += ", contrasena = %s"
        params.append(contrasena_hash)
    params.append(id_usuario)
    _, count = execute(f"UPDATE usuarios SET {campos} WHERE id_usuario = %s", tuple(params))
    return count


def eliminar(id_usuario):
    _, count = execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    return count


def admins_activos(excluir_id=None):
    row = query_one(
        "SELECT COUNT(*) AS total FROM usuarios WHERE rol = %s AND estado = 'Activo' AND id_usuario <> %s",
        (ROL_ADMIN, excluir_id or 0),
    )
    return int(row["total"]) if row else 0


def contar_movimientos(id_usuario):
    """Ventas y facturas registradas por el usuario (impiden borrarlo)."""
    row = query_one(
        """
        SELECT (SELECT COUNT(*) FROM venta WHERE id_usuario = %s)
             + (SELECT COUNT(*) FROM historial_facturas WHERE id_usuario = %s) AS total
        """,
        (id_usuario, id_usuario),
    )
    return int(row["total"]) if row else 0


def count_users():
    row = query_one("SELECT COUNT(*) AS total FROM usuarios")
    return int(row["total"]) if row else 0


# ---------- Bloqueo por intentos fallidos ----------

def get_attempt(clave):
    return query_one(
        "SELECT id, clave, intentos, bloqueado_hasta FROM intentos_acceso WHERE clave = %s",
        (clave,),
    )


def is_locked(clave):
    row = get_attempt(clave)
    if not row or not row.get("bloqueado_hasta"):
        return False
    return row["bloqueado_hasta"] > datetime.now()


def register_failed_attempt(clave, max_attempts, lock_minutes):
    row = get_attempt(clave)
    if row:
        intentos = int(row["intentos"]) + 1
        bloqueado = None
        if intentos >= max_attempts:
            bloqueado = datetime.now() + timedelta(minutes=lock_minutes)
            intentos = 0
        execute(
            "UPDATE intentos_acceso SET intentos = %s, bloqueado_hasta = %s WHERE clave = %s",
            (intentos, bloqueado, clave),
        )
        return bloqueado is not None
    execute(
        "INSERT INTO intentos_acceso (clave, intentos, bloqueado_hasta) VALUES (%s, %s, NULL)",
        (clave, 1),
    )
    return False


def clear_attempts(clave):
    execute("DELETE FROM intentos_acceso WHERE clave = %s", (clave,))
