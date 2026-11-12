from flask import Blueprint, render_template, flash

from data.dashboard import resumen
from database import DatabaseError
from utils.auth import es_admin, login_required

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    datos = {
        "clientes": 0,
        "productos": 0,
        "facturas": 0,
        "usuarios": 0,
        "empleados": 0,
        "proveedores": 0,
        "ventas_hoy": {"cantidad": 0, "ingresos": 0},
        "ventas_recientes": [],
        "stock_bajo": [],
    }
    try:
        datos.update(resumen(es_admin=es_admin()))
    except DatabaseError:
        flash("No se pudieron cargar los indicadores. Verifique MySQL.", "error")
    return render_template("dashboard.html", datos=datos)
