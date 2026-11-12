from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error, pooling
from flask import current_app, g

_pool = None


class DatabaseError(Exception):
    """Error controlado de acceso a MySQL."""


def init_pool(app=None):
    global _pool
    cfg = app.config if app is not None else current_app.config
    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name="vivero_paraiso",
            pool_size=5,
            pool_reset_session=True,
            host=cfg["MYSQL_HOST"],
            port=cfg["MYSQL_PORT"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
            database=cfg["MYSQL_DATABASE"],
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=False,
        )
    except Error as exc:
        _pool = None
        raise DatabaseError(
            "No fue posible crear el pool de conexiones a MySQL. "
            "Verifique host, puerto, usuario, contraseña y que la base exista."
        ) from exc
    return _pool


def get_pool():
    global _pool
    if _pool is None:
        init_pool()
    return _pool


def get_connection():
    if "db_conn" not in g:
        try:
            g.db_conn = get_pool().get_connection()
        except Error as exc:
            raise DatabaseError(
                "No fue posible conectar con MySQL. Revise que el servicio esté en ejecución."
            ) from exc
    return g.db_conn


def close_connection(_exc=None):
    conn = g.pop("db_conn", None)
    if conn is not None and conn.is_connected():
        conn.close()


def query_all(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    except Error as exc:
        raise DatabaseError("Error al consultar la base de datos.") from exc
    finally:
        cursor.close()


def query_one(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        return cursor.fetchone()
    except Error as exc:
        raise DatabaseError("Error al consultar la base de datos.") from exc
    finally:
        cursor.close()


def execute(sql, params=None, commit=True):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        last_id = cursor.lastrowid
        rowcount = cursor.rowcount
        if commit:
            conn.commit()
        return last_id, rowcount
    except Error as exc:
        conn.rollback()
        raise DatabaseError("Error al guardar los datos.") from exc
    finally:
        cursor.close()


@contextmanager
def transaction():
    """Agrupa varias sentencias: si una falla, se deshacen todas (commit o rollback)."""
    conn = get_connection()
    if conn.in_transaction:
        # Cierra la lectura implícita abierta por consultas anteriores de la misma petición
        conn.commit()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        conn.commit()
    except Error as exc:
        conn.rollback()
        raise DatabaseError("Error al guardar los datos.") from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def es_restriccion_fk(error):
    """True si el error viene de borrar un registro que otra tabla todavía usa (MySQL 1451)."""
    causa = getattr(error, "__cause__", None)
    return getattr(causa, "errno", None) == 1451


def ping():
    row = query_one("SELECT 1 AS ok")
    return bool(row and row.get("ok") == 1)
