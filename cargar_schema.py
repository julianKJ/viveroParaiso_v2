"""Crea la base y las tablas de schema.sql en el servidor MySQL configurado.

Sirve para servidores donde no hay cliente `mysql` a mano (por ejemplo Aiven).
Lee la conexión de .env o de las variables de entorno, igual que la app.
"""
import os
import sys

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv(os.getenv("ENV_FILE") or None)

from config import Config


def main():
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), encoding="utf-8") as fh:
        script = fh.read()
    # Sin comentarios de línea; el schema no usa DELIMITER, así que basta separar por ';'
    lineas = [l for l in script.splitlines() if not l.strip().startswith("--")]
    sentencias = [s.strip() for s in "\n".join(lineas).split(";") if s.strip()]

    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )
    except Error as exc:
        print(f"No se pudo conectar a MySQL en {Config.MYSQL_HOST}:{Config.MYSQL_PORT}: {exc.msg}")
        sys.exit(1)

    cursor = conn.cursor()
    try:
        for sentencia in sentencias:
            cursor.execute(sentencia)
        conn.commit()
    except Error as exc:
        print(f"Error ejecutando schema.sql: {exc.msg}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
    print(f"Tablas creadas en {Config.MYSQL_HOST} ({len(sentencias)} sentencias).")


if __name__ == "__main__":
    main()
