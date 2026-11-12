from data import productos, clientes, empleados, proveedores, ventas, facturas, usuarios


def resumen(es_admin=False):
    datos = {
        "clientes": clientes.total(),
        "productos": productos.total(),
        "facturas": facturas.total(),
        "ventas_hoy": ventas.resumen_hoy(),
        "ventas_recientes": ventas.recientes(),
        "stock_bajo": productos.stock_bajo(),
    }
    if es_admin:
        datos.update(
            {
                "usuarios": usuarios.count_users(),
                "empleados": empleados.total(),
                "proveedores": proveedores.total(),
            }
        )
    return datos
