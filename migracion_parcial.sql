-- Vivero El Paraíso de las Plantas
-- Migración de la versión anterior a la estructura del parcial final.
--
-- Úsela SOLO si su base se creó con el schema.sql anterior (tablas clientes,
-- productos, proveedores, empleados y usuarios con columna "username").
-- Conserva los datos: el rol admin pasa a administrador y empleado a vendedor,
-- y la cantidad de cada producto pasa a la nueva tabla stock.
-- Ejecútela una sola vez:  python cargar_schema.py migracion_parcial.sql
-- Haga un backup antes de ejecutarla.

USE vivero_paraiso;

-- ---------- usuarios ----------
ALTER TABLE usuarios MODIFY rol VARCHAR(30) NOT NULL DEFAULT 'vendedor';
UPDATE usuarios SET rol = IF(rol = 'admin', 'administrador', 'vendedor');
ALTER TABLE usuarios
    CHANGE COLUMN id id_usuario INT UNSIGNED NOT NULL AUTO_INCREMENT,
    CHANGE COLUMN username nombre_usuario VARCHAR(50) NOT NULL,
    CHANGE COLUMN password_hash contrasena VARCHAR(255) NOT NULL COMMENT 'Contraseña cifrada (hash)',
    ADD COLUMN estado VARCHAR(20) NOT NULL DEFAULT 'Activo' AFTER rol;
UPDATE usuarios SET estado = IF(activo = 1, 'Activo', 'Inactivo');
UPDATE usuarios SET email = LEFT(email, 100);
ALTER TABLE usuarios
    DROP COLUMN activo,
    DROP COLUMN creado_en,
    MODIFY email VARCHAR(100) NOT NULL,
    RENAME INDEX uk_usuarios_username TO uk_usuarios_nombre,
    ADD CONSTRAINT ck_usuarios_rol CHECK (rol IN ('administrador', 'vendedor')),
    ADD CONSTRAINT ck_usuarios_estado CHECK (estado IN ('Activo', 'Inactivo'));

-- ---------- clientes -> cliente ----------
ALTER TABLE clientes
    ADD COLUMN nombre VARCHAR(100) NULL AFTER id,
    ADD COLUMN ciudad VARCHAR(50) NOT NULL DEFAULT 'Sin especificar' AFTER direccion,
    ADD COLUMN pais VARCHAR(50) NOT NULL DEFAULT 'Colombia' AFTER ciudad;
UPDATE clientes
SET nombre = LEFT(CONCAT(nombres, ' ', apellidos), 100),
    correo = LEFT(correo, 100),
    direccion = LEFT(direccion, 150);
ALTER TABLE clientes DROP INDEX uk_clientes_documento;
ALTER TABLE clientes DROP INDEX idx_clientes_nombres;
ALTER TABLE clientes
    DROP COLUMN nombres,
    DROP COLUMN apellidos,
    DROP COLUMN tipo_documento,
    DROP COLUMN numero_documento,
    CHANGE COLUMN id id_cliente INT UNSIGNED NOT NULL AUTO_INCREMENT,
    CHANGE COLUMN nombre nombre VARCHAR(100) NOT NULL,
    CHANGE COLUMN correo email VARCHAR(100) NOT NULL AFTER nombre,
    CHANGE COLUMN direccion direccion VARCHAR(150) NOT NULL,
    ALTER COLUMN ciudad DROP DEFAULT,
    ALTER COLUMN pais DROP DEFAULT,
    RENAME INDEX uk_clientes_correo TO uk_cliente_email,
    ADD KEY idx_cliente_nombre (nombre),
    ADD KEY idx_cliente_pais (pais);
ALTER TABLE clientes MODIFY telefono VARCHAR(20) NOT NULL AFTER email;
RENAME TABLE clientes TO cliente;

-- ---------- proveedores -> proveedor ----------
ALTER TABLE productos DROP FOREIGN KEY fk_productos_proveedor;
ALTER TABLE proveedores
    CHANGE COLUMN id id_proveedor INT UNSIGNED NOT NULL AUTO_INCREMENT,
    RENAME INDEX uk_proveedores_nit TO uk_proveedor_nit,
    RENAME INDEX idx_proveedores_nombre TO idx_proveedor_nombre,
    RENAME INDEX idx_proveedores_contacto TO idx_proveedor_contacto;
RENAME TABLE proveedores TO proveedor;

-- ---------- empleados -> empleado ----------
ALTER TABLE empleados
    CHANGE COLUMN id id_empleado INT UNSIGNED NOT NULL AUTO_INCREMENT,
    RENAME INDEX uk_empleados_documento TO uk_empleado_documento,
    RENAME INDEX uk_empleados_correo TO uk_empleado_correo,
    RENAME INDEX idx_empleados_nombres TO idx_empleado_nombres,
    RENAME INDEX idx_empleados_cargo TO idx_empleado_cargo;
RENAME TABLE empleados TO empleado;

-- ---------- productos -> producto ----------
ALTER TABLE productos
    CHANGE COLUMN id id_producto INT UNSIGNED NOT NULL AUTO_INCREMENT,
    CHANGE COLUMN proveedor_id id_proveedor INT UNSIGNED NOT NULL,
    RENAME INDEX idx_productos_nombre TO idx_producto_nombre,
    RENAME INDEX idx_productos_categoria TO idx_producto_categoria,
    RENAME INDEX fk_productos_proveedor TO fk_producto_proveedor;
RENAME TABLE productos TO producto;
ALTER TABLE producto
    ADD CONSTRAINT fk_producto_proveedor
        FOREIGN KEY (id_proveedor) REFERENCES proveedor (id_proveedor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT;

-- ---------- stock (sale de las columnas del producto) ----------
CREATE TABLE stock (
    id_stock INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_producto INT UNSIGNED NOT NULL,
    cantidad_disponible INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 0,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_stock),
    UNIQUE KEY uk_stock_producto (id_producto),
    KEY idx_stock_cantidad (cantidad_disponible, stock_minimo),
    CONSTRAINT ck_stock_cantidad CHECK (cantidad_disponible >= 0),
    CONSTRAINT ck_stock_minimo CHECK (stock_minimo >= 0),
    CONSTRAINT fk_stock_producto
        FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO stock (id_producto, cantidad_disponible, stock_minimo)
SELECT id_producto, GREATEST(cantidad_disponible, 0), GREATEST(stock_minimo, 0)
FROM producto;

ALTER TABLE producto DROP INDEX idx_productos_stock;
ALTER TABLE producto
    DROP COLUMN cantidad_disponible,
    DROP COLUMN stock_minimo;

-- ---------- venta ----------
CREATE TABLE venta (
    id_venta INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_cliente INT UNSIGNED NOT NULL,
    id_producto INT UNSIGNED NOT NULL,
    id_usuario INT UNSIGNED NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(12, 2) NOT NULL,
    total DECIMAL(14, 2) NOT NULL,
    fecha_venta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_venta),
    KEY idx_venta_fecha (fecha_venta),
    CONSTRAINT ck_venta_cantidad CHECK (cantidad > 0),
    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_venta_producto
        FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_venta_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------- historial_facturas ----------
CREATE TABLE historial_facturas (
    id_factura INT UNSIGNED NOT NULL AUTO_INCREMENT,
    numero_factura VARCHAR(20) NOT NULL,
    id_venta INT UNSIGNED NOT NULL,
    id_usuario INT UNSIGNED NOT NULL COMMENT 'Usuario que generó la factura',
    cliente_nombre VARCHAR(100) NOT NULL,
    cliente_email VARCHAR(100) NOT NULL,
    cliente_direccion VARCHAR(150) NOT NULL,
    cliente_ciudad VARCHAR(50) NOT NULL,
    cliente_pais VARCHAR(50) NOT NULL,
    producto_nombre VARCHAR(150) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(12, 2) NOT NULL,
    total DECIMAL(14, 2) NOT NULL,
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_factura),
    UNIQUE KEY uk_factura_numero (numero_factura),
    UNIQUE KEY uk_factura_venta (id_venta),
    KEY idx_factura_fecha (fecha_emision),
    CONSTRAINT fk_factura_venta
        FOREIGN KEY (id_venta) REFERENCES venta (id_venta)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_factura_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
