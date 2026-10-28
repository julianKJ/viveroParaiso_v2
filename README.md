# 🌿 Vivero El Paraíso de las Plantas

> Sistema de información web robusto y seguro para la gestión integral de inventario, clientes, empleados y proveedores en viveros y centros de jardinería.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![HTML5/CSS3](https://img.shields.io/badge/Frontend-HTML5%20%2F%20CSS3-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-success?style=for-the-badge)](#)

---

## 📋 Tabla de Contenidos

1. [Características Principales](#-características-principales)
2. [Stack Tecnológico](#-stack-tecnológico)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Requisitos Previos](#-requisitos-previos)
5. [Guía Paso a Paso: Instalación y Puesta en Marcha](#-guía-paso-a-paso-instalación-y-puesta-en-marcha)
6. [Credenciales de Acceso](#-credenciales-de-acceso)
7. [Seguridad Implementada](#-seguridad-implementada)
8. [Pruebas Automatizadas](#-pruebas-automatizadas)
9. [Resolución de Problemas Frecuentes](#-resolución-de-problemas-frecuentes)

---

## ✨ Características Principales

* **📊 Dashboard de Indicadores:** Métricas en tiempo real de productos, clientes, colaboradores, proveedores y alertas visuales de inventario bajo stock mínimo.
* **🌱 Gestión de Inventario:** Catálogo categorizado de plantas (interior, exterior, suculentas, flores) e insumos con control de precios de compra/venta y alertas de reposición.
* **🤝 Proveedores y Clientes:** Registro detallado de contactos con validación de documentos y protección de integridad referencial (no permite borrar proveedores con productos activos).
* **👥 Gestión de Personal y Roles (RBAC):** Módulo de empleados protegido por control de acceso basado en roles (`admin` / `empleado`).
* **🛡️ Seguridad Integral:** Protección contra CSRF, hashing con algoritmos modernos (Werkzeug/scrypt), consultas preparadas anti-SQLi y rate limiting contra ataques de fuerza bruta.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, Flask 3.0 | Estructura modular basada en Blueprints y Application Factory |
| **Persistencia** | MySQL 8.0+ | `mysql-connector-python` con Connection Pooling |
| **Frontend** | Jinja2, HTML5, CSS3, FontAwesome 6 | Interfaz responsiva, diseño limpio sin dependencias pesadas de JS |
| **Seguridad** | Flask-WTF, Werkzeug | Manejo seguro de sesiones, tokens CSRF y hashing criptográfico |
| **Testing** | Pytest | Pruebas unitarias de enrutamiento, autenticación y validadores |

---

## 📁 Estructura del Proyecto

```text
viveroParaiso_v2/
├── blueprints/             # Módulos de la aplicación (Auth, Dashboard, Productos, etc.)
│   ├── auth.py
│   ├── clientes.py
│   ├── dashboard.py
│   ├── empleados.py
│   ├── productos.py
│   └── proveedores.py
├── data/                   # Capa de acceso a datos (queries y transacciones SQL)
│   ├── clientes.py
│   ├── dashboard.py
│   ├── empleados.py
│   ├── productos.py
│   ├── proveedores.py
│   └── usuarios.py
├── static/                 # Recursos estáticos (CSS, SVGs, imágenes)
│   ├── css/
│   └── img/
├── templates/              # Vistas HTML renderizadas con Jinja2
│   ├── componentes/
│   ├── errores/
│   └── *.html
├── tests/                  # Suite de pruebas automatizadas
│   ├── test_auth_routes.py
│   └── test_validators.py
├── utils/                  # Helpers, decoradores de autenticación y validaciones
├── app.py                  # Punto de entrada de la aplicación
├── config.py               # Gestión centralizada de configuración
├── database.py             # Pool de conexiones MySQL
├── init_admin.py           # Script CLI para crear el superusuario inicial
├── seed.py                 # Datos de prueba para demostración
├── schema.sql              # Estructura DDL de la base de datos
├── requirements.txt        # Dependencias de Python
├── run.bat                 # Lanzador automático de 1 clic (Windows)
├── run.ps1                 # Script de arranque para PowerShell
└── .env.example            # Plantilla de variables de entorno
```

---

## ⚡ Inicio Rápido Automático (Recomendado)

Si estás en **Windows**, ¡no necesitas configurar nada a mano!

Simplemente haz doble clic en **`run.bat`** (o ejecuta en tu terminal `.\run.bat` o `.\run.ps1`).

El script automáticamente:
1. Creará el archivo `.env` si aún no existe.
2. Detectará tu versión de Python (usando `py` o `python`).
3. Creará el entorno virtual `.venv` y descargará las dependencias.
4. Iniciará el servidor en **http://127.0.0.1:5000** listo para probar.

---

## ⚙️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

* **Python 3.11 o superior** (marcando la opción *"Add python.exe to PATH"* durante la instalación).
* **MySQL Server 8.0 o superior** (y opcionalmente MySQL Workbench).
* **Git** (opcional, para clonar el repositorio).
* **PowerShell** (Windows) o **Bash / Zsh** (Linux / macOS).

---

## 🚀 Guía Paso a Paso: Instalación y Puesta en Marcha

Sigue estos pasos en orden para levantar la aplicación en tu entorno local:

### 1. Clonar el repositorio y entrar al directorio

Abre tu terminal favorita (por ejemplo PowerShell) y navega a tu carpeta de trabajo:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd viveroParaiso_v2
```

### 2. Crear y activar el entorno virtual

Crea un entorno virtual aislado para instalar las dependencias:

**En Windows (PowerShell):**
```powershell
# Usa python o el lanzador oficial py:
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
> *Tip:* Si `python` te muestra el mensaje *"Python was not found..."* de la Microsoft Store, usa siempre `py -m venv .venv`.  
> *Nota:* Si PowerShell muestra una restricción de ejecución de scripts, ejecuta:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

**En Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias

Con el entorno virtual activado, actualiza pip e instala los paquetes requeridos:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copia la plantilla `.env.example` para generar tu archivo `.env`:

**En Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**En Linux / macOS:**
```bash
cp .env.example .env
```

Abre el archivo `.env` con tu editor y configura:
* `SECRET_KEY`: Llave de sesión criptográfica (puedes generar una con `python -c "import secrets; print(secrets.token_hex(32))"`).
* `MYSQL_USER`: Tu usuario de MySQL (comúnmente `root`).
* `MYSQL_PASSWORD`: La contraseña de tu servidor MySQL.
* `MYSQL_DATABASE`: Nombre de la base de datos (por defecto `vivero_paraiso`).

### 5. Crear la base de datos y tablas

Asegúrate de que el servicio de MySQL esté iniciado. Luego, carga el archivo `schema.sql`:

**Opción A — Desde PowerShell:**
```powershell
Get-Content .\schema.sql | mysql -u root -p
```

**Opción B — Desde MySQL Workbench / DBeaver:**
Abre una conexión a tu servidor local, abre el archivo `schema.sql` y ejecútalo por completo.

### 6. Cargar datos iniciales y usuario Administrador

Para poblar la base de datos con los registros base y el usuario administrador:

1. **Crear el Administrador:**
   ```powershell
   python init_admin.py
   ```
   *(Lee las credenciales de `ADMIN_USERNAME` / `ADMIN_PASSWORD` en `.env` o te las solicitará interactivamente).*

2. **Cargar datos de prueba (Opcional):**
   ```powershell
   python seed.py
   ```
   *(Inserta clientes, proveedores con sus NITs, plantas y alertas de stock de demostración).*

### 7. Iniciar el servidor de desarrollo

Ejecuta la aplicación Flask:

```powershell
python app.py
```

Verás una salida similar a:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 Press CTRL+C to quit
```

### 8. Acceder a la plataforma

Abre tu navegador web e ingresa a:

👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Credenciales de Acceso

| Tipo de Acceso | Usuario / Identificador | Contraseña | Rol | Notas |
| :--- | :--- | :--- | :--- | :--- |
| **Producción / Normal** | Configurado en `init_admin.py` | Configurada al inicializar | `admin` | Requiere MySQL activo con tablas creadas. |
| **Pruebas / Interno (Bypass)** | `admin` | `admin123` | `admin` | Acceso rápido para testeo y revisión de vistas sin fricción. |

---

## 🔒 Seguridad Implementada

* **Protección CSRF:** Todos los formularios POST exigen un token criptográfico generado por `Flask-WTF`.
* **Hash Criptográfico:** Contraseñas protegidas mediante algoritmos de hash seguros provistos por `werkzeug.security` (`scrypt`/`pbkdf2`), nunca en texto plano.
* **Consultas Parametrizadas:** Protección nativa contra inyecciones SQL mediante tuplas de parámetros en `mysql-connector-python`.
* **Mitigación de Fuerza Bruta:** Bloqueo temporal de cuentas tras 5 intentos fallidos consecutivos durante 15 minutos.
* **Control de Sesiones:** Cookies de sesión configuradas con flags `HTTPOnly` y `SameSite=Lax`.

---

## 🧪 Pruebas Automatizadas

El proyecto incluye una suite de pruebas con **pytest** para asegurar la integridad de rutas y utilidades:

```powershell
pytest -v
```

---

## ❓ Resolución de Problemas Frecuentes

<details>
<summary><b>1. Error: "No fue posible conectar con MySQL"</b></summary>

* Verifica que el servicio de MySQL esté corriendo:
  ```powershell
  Get-Service *mysql*
  ```
  Si está detenido, inícialo con `Start-Service mysql` (o desde los Servicios de Windows).
* Confirma que los datos en `.env` (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_PORT`) coincidan con tu configuración local.
* Asegúrate de haber ejecutado `schema.sql`.
</details>

<details>
<summary><b>2. Error: "SECRET_KEY no está definida"</b></summary>

* Asegúrate de haber creado el archivo `.env` en la raíz del proyecto a partir de `.env.example`.
</details>

<details>
<summary><b>3. La política de ejecución de PowerShell bloquea el virtualenv</b></summary>

* Ejecuta PowerShell como usuario estándar y habilita la ejecución local:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
</details>

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos y profesionales para el vivero **El Paraíso de las Plantas**.
Libre para uso educativo y de referencia.
