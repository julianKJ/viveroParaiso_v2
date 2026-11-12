import os
from decimal import Decimal
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from database import close_connection, DatabaseError
from utils.validators import ROL_ADMIN

load_dotenv()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    from config import Config

    app.config.from_object(Config)
    if app.config["TRUST_PROXY"]:
        # Toma solo la IP que agregó el proxy de confianza, no las que envía el visitante
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    csrf.init_app(app)

    from blueprints.auth import bp as auth_bp
    from blueprints.dashboard import bp as dashboard_bp
    from blueprints.productos import bp as productos_bp
    from blueprints.clientes import bp as clientes_bp
    from blueprints.empleados import bp as empleados_bp
    from blueprints.proveedores import bp as proveedores_bp
    from blueprints.ventas import bp as ventas_bp
    from blueprints.usuarios import bp as usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(empleados_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(usuarios_bp)

    app.teardown_appcontext(close_connection)

    def imagen_producto(producto_id):
        """Devuelve la ruta de static/img/productos/<id>.<ext> si existe, o None."""
        for ext in ("webp", "jpg", "jpeg", "png"):
            relativa = f"img/productos/{producto_id}.{ext}"
            if os.path.exists(os.path.join(app.static_folder, relativa)):
                return relativa
        return None

    @app.template_filter("pesos")
    def pesos(valor, decimales=0):
        """Formato de moneda colombiano: $ 1.234.567 (punto de miles, coma decimal)."""
        texto = f"{Decimal(str(valor or 0)):,.{decimales}f}"
        return "$ " + texto.replace(",", "_").replace(".", ",").replace("_", ".")

    @app.context_processor
    def inject_globals():
        return {
            "vivero_nombre": "Vivero El Paraíso de las Plantas",
            "imagen_producto": imagen_producto,
            "es_admin": session.get("rol") == ROL_ADMIN,
            "usuario_actual": {
                "id": session.get("user_id"),
                "username": session.get("username"),
                "email": session.get("email"),
                "rol": session.get("rol"),
            }
            if session.get("user_id")
            else None,
        }

    @app.errorhandler(CSRFError)
    def handle_csrf(_error):
        return render_template("errores/403.html", mensaje="La sesión del formulario expiró. Recargue la página."), 400

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errores/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errores/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("errores/500.html"), 500

    @app.errorhandler(DatabaseError)
    def database_error(_error):
        return render_template("errores/500.html"), 500

    @app.route("/inicio")
    def inicio():
        if session.get("user_id"):
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    return app


app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") in {"1", "true", "True"}
    app.run(host="127.0.0.1", port=5000, debug=debug)
