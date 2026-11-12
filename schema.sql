-- Vivero El Paraíso de las Plantas
-- Script de creación de la base de datos y tablas (estructura del parcial final).
--
-- Módulo 0 y 3: usuarios (roles administrador y vendedor).
-- Módulo 1: cliente.
-- Módulo 2: producto, stock, venta e historial_facturas.
-- Tablas de apoyo: proveedor, empleado e intentos_acceso.
--
-- Para convertir una base creada con la versión anterior use migracion_parcial.sql.

CREATE DATABASE IF NOT EXISTS vivero_paraiso
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE vivero_paraiso;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre_usuario VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    contrasena VARCHAR(255) NOT NULL COMMENT 'Contraseña cifrada (hash)',
    rol VARCHAR(30) NOT NULL DEFAULT 'vendedor',
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    PRIMARY KEY (id_usuario),
    UNIQUE KEY uk_usuarios_email (email),
    UNIQUE KEY uk_usuarios_nombre (nombre_usuario),
    CONSTRAINT ck_usuarios_rol CHECK (rol IN ('administrador', 'vendedor')),
    CONSTRAINT ck_usuarios_estado CHECK (estado IN ('Activo', 'Inactivo'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    pais VARCHAR(50) NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente),
    UNIQUE KEY uk_cliente_email (email),
    KEY idx_cliente_nombre (nombre),
    KEY idx_cliente_pais (pais)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS proveedor (
    id_proveedor INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre_empresa VARCHAR(150) NOT NULL,
    nit VARCHAR(30) NOT NULL,
    persona_contacto VARCHAR(120) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    productos_suministrados TEXT NULL,
    estado ENUM('Activo', 'Inactivo') NOT NULL DEFAULT 'Activo',
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_proveedor),
    UNIQUE KEY uk_proveedor_nit (nit),
    KEY idx_proveedor_nombre (nombre_empresa),
    KEY idx_proveedor_contacto (persona_contacto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS empleado (
    id_empleado INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombres VARCHAR(80) NOT NULL,
    apellidos VARCHAR(80) NOT NULL,
    tipo_documento ENUM('CC', 'CE', 'NIT', 'Pasaporte', 'TI') NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    cargo VARCHAR(80) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    fecha_contratacion DATE NOT NULL,
    estado_laboral ENUM('Activo', 'Inactivo', 'Vacaciones') NOT NULL DEFAULT 'Activo',
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_empleado),
    UNIQUE KEY uk_empleado_documento (numero_documento),
    UNIQUE KEY uk_empleado_correo (correo),
    KEY idx_empleado_nombres (nombres, apellidos),
    KEY idx_empleado_cargo (cargo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS producto (
    id_producto INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    descripcion TEXT NULL,
    precio_compra DECIMAL(12, 2) NOT NULL,
    precio_venta DECIMAL(12, 2) NOT NULL,
    id_proveedor INT UNSIGNED NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_producto),
    KEY idx_producto_nombre (nombre),
    KEY idx_producto_categoria (categoria),
    CONSTRAINT fk_producto_proveedor
        FOREIGN KEY (id_proveedor) REFERENCES proveedor (id_proveedor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Existencias de cada producto: disminuye con cada venta.
CREATE TABLE IF NOT EXISTS stock (
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

-- Venta de un producto a un cliente, registrada por un usuario.
CREATE TABLE IF NOT EXISTS venta (
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

-- Facturas generadas. Guarda una copia de los datos para que la factura
-- no cambie si después se edita el cliente o el producto.
CREATE TABLE IF NOT EXISTS historial_facturas (
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

CREATE TABLE IF NOT EXISTS intentos_acceso (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    clave VARCHAR(255) NOT NULL,
    intentos INT NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_intentos_clave (clave)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
