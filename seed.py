"""Carga datos de demostración. Requiere que la base y el administrador existan."""
import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv(os.getenv("ENV_FILE") or None)

from flask import Flask
from config import Config
from database import init_pool, close_connection, DatabaseError, query_one
from data import proveedores, productos, clientes, empleados


def main():
    app = Flask(__name__)
    app.config.from_object(Config)
    with app.app_context():
        try:
            init_pool(app)
        except DatabaseError as exc:
            print(str(exc))
            return

        if query_one("SELECT id FROM proveedores LIMIT 1"):
            print("Ya hay datos de demostración. No se insertó información duplicada.")
            return

        p1 = proveedores.crear(
            {
                "nombre_empresa": "Viveros del Café S.A.S.",
                "nit": "900123456-1",
                "persona_contacto": "Laura Méndez",
                "telefono": "3105550101",
                "correo": "contacto@viverosdelcafe.com",
                "direccion": "Km 4 vía Armenia, Quindío",
                "productos_suministrados": "Plantas de interior, suculentas y macetas.",
                "estado": "Activo",
            }
        )
        p2 = proveedores.crear(
            {
                "nombre_empresa": "Semillas Andinas",
                "nit": "800987654-2",
                "persona_contacto": "Carlos Pérez",
                "telefono": "3205550199",
                "correo": "ventas@semillasandinas.co",
                "direccion": "Cra 15 # 8-20, Bogotá",
                "productos_suministrados": "Semillas, abonos y herramientas.",
                "estado": "Activo",
            }
        )

        productos.crear(
            {
                "nombre": "Monstera deliciosa",
                "categoria": "Plantas de interior",
                "descripcion": "Planta tropical de hojas grandes, ideal para interiores iluminados.",
                "precio_compra": 28000,
                "precio_venta": 45000,
                "cantidad_disponible": 12,
                "stock_minimo": 5,
                "proveedor_id": p1,
            }
        )
        productos.crear(
            {
                "nombre": "Suculenta Echeveria",
                "categoria": "Suculentas",
                "descripcion": "Roseta compacta de bajo mantenimiento.",
                "precio_compra": 4000,
                "precio_venta": 9000,
                "cantidad_disponible": 3,
                "stock_minimo": 8,
                "proveedor_id": p1,
            }
        )
        productos.crear(
            {
                "nombre": "Abono orgánico 2kg",
                "categoria": "Abonos",
                "descripcion": "Mezcla enriquecida para huerta y jardín.",
                "precio_compra": 8000,
                "precio_venta": 14500,
                "cantidad_disponible": 40,
                "stock_minimo": 10,
                "proveedor_id": p2,
            }
        )

        clientes.crear(
            {
                "nombres": "María Camila",
                "apellidos": "Gómez Ruiz",
                "tipo_documento": "CC",
                "numero_documento": "1020304050",
                "telefono": "3001112233",
                "correo": "maria.gomez@correo.com",
                "direccion": "Calle 12 # 4-18, Armenia",
            }
        )
        empleados.crear(
            {
                "nombres": "Andrés",
                "apellidos": "López",
                "tipo_documento": "CC",
                "numero_documento": "1098765432",
                "cargo": "Jardinero",
                "telefono": "3124445566",
                "correo": "andres.lopez@viveroparaiso.local",
                "fecha_contratacion": date.today() - timedelta(days=180),
                "estado_laboral": "Activo",
            }
        )
        print("Datos de demostración insertados.")
        close_connection()


if __name__ == "__main__":
    main()
