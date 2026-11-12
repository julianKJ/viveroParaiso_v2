"""Carga datos de demostración: proveedores, productos con stock, clientes de varios países y un empleado.

Requiere que la base exista (schema.sql). Los usuarios se crean con init_admin.py y el módulo 3.
"""
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

        if query_one("SELECT id_proveedor FROM proveedor LIMIT 1"):
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
                "id_proveedor": p1,
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
                "id_proveedor": p1,
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
                "id_proveedor": p2,
            }
        )

        demo_clientes = [
            ("María Camila Gómez Ruiz", "maria.gomez@correo.com", "3001112233", "Calle 12 # 4-18", "Villavicencio", "Colombia"),
            ("Jorge Andrés Rincón", "jorge.rincon@correo.com", "3157778899", "Cra 33 # 15-40", "Bogotá", "Colombia"),
            ("Luisa Fernanda Ortiz", "luisa.ortiz@correo.com", "3204445566", "Av. 40 # 22-10", "Acacías", "Colombia"),
            ("Carlos Eduardo Pérez", "carlos.perez@correo.ve", "+58 4121234567", "Calle Bolívar 45", "Caracas", "Venezuela"),
            ("Ana Lucía Torres", "ana.torres@correo.ec", "+593 991234567", "Av. Amazonas N34", "Quito", "Ecuador"),
            ("Diego Ramírez Soto", "diego.ramirez@correo.mx", "+52 5512345678", "Insurgentes Sur 1200", "Ciudad de México", "México"),
        ]
        for nombre, email, telefono, direccion, ciudad, pais in demo_clientes:
            clientes.crear(
                {
                    "nombre": nombre,
                    "email": email,
                    "telefono": telefono,
                    "direccion": direccion,
                    "ciudad": ciudad,
                    "pais": pais,
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
