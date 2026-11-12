"""Ejecuta un script SQL (por defecto schema.sql) en el servidor MySQL configurado.

Sirve para servidores donde no hay cliente `mysql` a mano (por ejemplo Aiven).
Lee la conexión de .env o de las variables de entorno, igual que la app.

    python cargar_schema.py                         # crea la base y las tablas
    python cargar_schema.py migracion_parcial.sql   # migra una base de la versión anterior
"""
import os
import sys

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv(os.getenv("ENV_FILE") or None)

from config import Config


def main():
    archivo = sys.argv[1] if len(sys.argv) > 1 else "schema.sql"
    ruta = archivo if os.path.isabs(archivo) else os.path.join(os.path.dirname(os.path.abspath(__file__)), archivo)
    with open(ruta, encoding="utf-8") as fh:
        script = fh.read()
    # Sin comentarios de línea; los scripts no usan DELIMITER, así que basta separar por ';'
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
        for numero, sentencia in enumerate(sentencias, start=1):
            try:
                cursor.execute(sentencia)
            except Error as exc:
                resumen = " ".join(sentencia.split())[:160]
                print(f"Error en la sentencia {numero} de {archivo}: {exc.msg}")
                print(f"  {resumen}")
                sys.exit(1)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    print(f"{archivo} ejecutado en {Config.MYSQL_HOST} ({len(sentencias)} sentencias).")


if __name__ == "__main__":
    main()
