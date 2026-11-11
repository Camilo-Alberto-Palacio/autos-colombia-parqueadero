-- ====================================================================
-- PARQUEADERO AUTOS COLOMBIA 24/7 - SISTEMA DE CONTROL DE ACCESO
-- MODELO FÍSICO DE BASE DE DATOS (DDL & DML) - ITERACIONES 1, 2 Y 3 UNIFICADAS
-- Asignatura: Ingeniería de Software - PREICA2602B020053
-- Docente: Reinaldo Rojas | Grupo: 25
-- Integrantes:
--   - Camilo Alberto Palacios Turriago
--   - Adriana Andrea Agudelo Agudelo
--   - Juan Daniel Pulgarin García
-- ====================================================================

-- 1. TABLA: PROPIETARIO / CLIENTE ABONADO (Gestión de Abonados)
CREATE TABLE IF NOT EXISTS propietario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento VARCHAR(20) NOT NULL UNIQUE,
    nombre_completo VARCHAR(120) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    direccion VARCHAR(120),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: VEHICULO (Catálogo de Automotores)
CREATE TABLE IF NOT EXISTS vehiculo (
    placa VARCHAR(10) PRIMARY KEY,
    tipo_vehiculo VARCHAR(10) NOT NULL CHECK (tipo_vehiculo IN ('CARRO', 'MOTO')),
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    propietario_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (propietario_id) REFERENCES propietario(id) ON DELETE RESTRICT
);

-- 3. TABLA: MENSUALIDAD (Contratos de Parqueo por Mensualidad)
CREATE TABLE IF NOT EXISTS mensualidad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_placa VARCHAR(10) NOT NULL,
    fecha_pago DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    valor_pagado DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(15) NOT NULL CHECK (estado IN ('ACTIVA', 'VENCIDA', 'CANCELADA')),
    FOREIGN KEY (vehiculo_placa) REFERENCES vehiculo(placa) ON DELETE CASCADE
);

-- 4. TABLA: CELDA (80 Celdas: 10 Motos M-01 a M-10, 70 Carros C-01 a C-70)
CREATE TABLE IF NOT EXISTS celda (
    codigo VARCHAR(10) PRIMARY KEY,
    tipo_permitido VARCHAR(10) NOT NULL CHECK (tipo_permitido IN ('CARRO', 'MOTO')),
    estado VARCHAR(15) NOT NULL DEFAULT 'DISPONIBLE' CHECK (estado IN ('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO', 'INACTIVA')),
    piso INTEGER DEFAULT 1,
    zona VARCHAR(20) DEFAULT 'PRINCIPAL',
    motivo_bloqueo TEXT
);

-- 5. TABLA: USUARIO (Control de Acceso al Sistema, Roles y Permisos)
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('ADMIN', 'OPERARIO', 'AUDITOR')),
    cargo VARCHAR(60) DEFAULT 'Operador de Turno',
    activo BOOLEAN NOT NULL DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME
);

-- 6. TABLA: REGISTRO_ACCESO (Control Operativo de Entrada y Salida 24/7)
CREATE TABLE IF NOT EXISTS registro_acceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_placa VARCHAR(10) NOT NULL,
    celda_codigo VARCHAR(10) NOT NULL,
    fecha_ingreso DATETIME NOT NULL,
    fecha_salida DATETIME,
    estado VARCHAR(15) NOT NULL DEFAULT 'ADENTRO' CHECK (estado IN ('ADENTRO', 'FINALIZADO')),
    observaciones TEXT,
    usuario_id INTEGER,
    FOREIGN KEY (vehiculo_placa) REFERENCES vehiculo(placa) ON DELETE RESTRICT,
    FOREIGN KEY (celda_codigo) REFERENCES celda(codigo) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL
);

-- 7. TABLA: HISTORIAL_CELDA (Trazabilidad y Mantenimiento de Celdas)
CREATE TABLE IF NOT EXISTS historial_celda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    celda_codigo VARCHAR(10) NOT NULL,
    estado_anterior VARCHAR(15) NOT NULL,
    estado_nuevo VARCHAR(15) NOT NULL,
    motivo TEXT,
    usuario_id INTEGER,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (celda_codigo) REFERENCES celda(codigo) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL
);

-- 8. TABLA: AUDITORIA_ACCION (Trazabilidad y Seguridad 24/7)
CREATE TABLE IF NOT EXISTS auditoria_accion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalle TEXT,
    ip_terminal VARCHAR(50) DEFAULT 'Terminal Local',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL
);

-- 9. TABLA: PAGO (Libro Mayor Inmutable de Recaudos y Mensualidades - Iteración 3)
CREATE TABLE IF NOT EXISTS pago (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_recibo VARCHAR(30) NOT NULL UNIQUE,
    vehiculo_placa VARCHAR(10) NOT NULL,
    mensualidad_id INTEGER NOT NULL,
    fecha_pago DATE NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    meses_pagados INTEGER NOT NULL DEFAULT 1 CHECK (meses_pagados >= 1 AND meses_pagados <= 12),
    valor_pagado DECIMAL(10, 2) NOT NULL CHECK (valor_pagado > 0),
    metodo_pago VARCHAR(25) NOT NULL CHECK (metodo_pago IN ('EFECTIVO', 'TRANSFERENCIA_BANCARIA', 'CODIGO_QR', 'CONSIGNACION')),
    referencia_comprobante VARCHAR(80),
    tipo_aplicacion VARCHAR(30) NOT NULL CHECK (tipo_aplicacion IN ('PAGO_ANTICIPADO', 'PAGO_PUNTUAL', 'MORA_CONSECUTIVA', 'INICIAL_REACTIVACION')),
    estado VARCHAR(15) NOT NULL DEFAULT 'CONFIRMADO' CHECK (estado IN ('CONFIRMADO', 'ANULADO')),
    observaciones TEXT,
    usuario_id INTEGER,
    FOREIGN KEY (vehiculo_placa) REFERENCES vehiculo(placa) ON DELETE RESTRICT,
    FOREIGN KEY (mensualidad_id) REFERENCES mensualidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL
);

-- ÍNDICES DE ALTO RENDIMIENTO
CREATE INDEX IF NOT EXISTS idx_vehiculo_placa ON vehiculo(placa);
CREATE INDEX IF NOT EXISTS idx_celda_estado_tipo ON celda(tipo_permitido, estado);
CREATE INDEX IF NOT EXISTS idx_registro_activo ON registro_acceso(vehiculo_placa, estado);
CREATE INDEX IF NOT EXISTS idx_mensualidad_placa ON mensualidad(vehiculo_placa, fecha_vencimiento);
CREATE INDEX IF NOT EXISTS idx_usuario_user ON usuario(username);
CREATE INDEX IF NOT EXISTS idx_historial_celda ON historial_celda(celda_codigo);
CREATE INDEX IF NOT EXISTS idx_pago_placa ON pago(vehiculo_placa, fecha_pago DESC);
CREATE INDEX IF NOT EXISTS idx_pago_fecha ON pago(fecha_pago, estado);
CREATE INDEX IF NOT EXISTS idx_pago_recibo ON pago(numero_recibo);

-- ====================================================================
-- DATOS SEMILLA: CELDAS, CLIENTES, VEHÍCULOS Y USUARIOS
-- ====================================================================

-- 10 Celdas de Motos: M-01 a M-10
INSERT OR IGNORE INTO celda (codigo, tipo_permitido, estado, piso, zona) VALUES
('M-01', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-02', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-03', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-04', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-05', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-06', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-07', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-08', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-09', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS'),
('M-10', 'MOTO', 'DISPONIBLE', 1, 'ZONA MOTOS');

-- 70 Celdas de Carros: C-01 a C-70
INSERT OR IGNORE INTO celda (codigo, tipo_permitido, estado, piso, zona) VALUES
('C-01', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-02', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-03', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-04', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-05', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-06', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-07', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-08', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-09', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-10', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-11', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-12', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-13', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-14', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-15', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-16', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-17', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-18', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-19', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-20', 'CARRO', 'DISPONIBLE', 1, 'ZONA A'),
('C-21', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-22', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-23', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-24', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-25', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-26', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-27', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-28', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-29', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-30', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-31', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-32', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-33', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-34', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-35', 'CARRO', 'DISPONIBLE', 1, 'ZONA B'),
('C-36', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-37', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-38', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-39', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-40', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-41', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-42', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-43', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-44', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-45', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-46', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-47', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-48', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-49', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-50', 'CARRO', 'DISPONIBLE', 1, 'ZONA C'),
('C-51', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-52', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-53', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-54', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-55', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-56', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-57', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-58', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-59', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-60', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA D'),
('C-61', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-62', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-63', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-64', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-65', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-66', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-67', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-68', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-69', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E'),
('C-70', 'CARRO', 'DISPONIBLE', 2, 'PISO 2 - ZONA E');

-- Usuarios Semilla (Claves SHA-256 verificadas)
-- admin: admin123       -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- adriana_op: operario123 -> ea66d0295003394ff7f847590fe43af491ded28bb3837d543d55dfa130c9b2f3
-- daniel_op: operario123  -> ea66d0295003394ff7f847590fe43af491ded28bb3837d543d55dfa130c9b2f3
-- auditor: auditor123     -> 5b92db4dfb561dc69c949f34d36f5db0f8b30811be3a2949d85c5001279e9b1a
INSERT OR IGNORE INTO usuario (id, username, password_hash, nombre_completo, email, rol, cargo, activo) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Camilo Alberto Palacios Turriago', 'camilo.palacios@autoscolombia.com', 'ADMIN', 'Administrador General', 1),
(2, 'adriana_op', 'ea66d0295003394ff7f847590fe43af491ded28bb3837d543d55dfa130c9b2f3', 'Adriana Andrea Agudelo Agudelo', 'adriana.agudelo@autoscolombia.com', 'OPERARIO', 'Operador de Turno Norte', 1),
(3, 'daniel_op', 'ea66d0295003394ff7f847590fe43af491ded28bb3837d543d55dfa130c9b2f3', 'Juan Daniel Pulgarin García', 'daniel.pulgarin@autoscolombia.com', 'OPERARIO', 'Operador de Turno Sur', 1),
(4, 'auditor', '5b92db4dfb561dc69c949f34d36f5db0f8b30811be3a2949d85c5001279e9b1a', 'Auditor de Calidad y Seguridad', 'auditoria@autoscolombia.com', 'AUDITOR', 'Auditor de Sistemas', 1);

-- Propietarios de prueba
INSERT OR IGNORE INTO propietario (id, documento, nombre_completo, telefono, email, direccion) VALUES
(1, '1020304050', 'Juan Carlos Pérez', '3104567890', 'juan.perez@email.com', 'Calle 50 # 45-20, Medellín'),
(2, '1030405060', 'David Gómez', '3129876543', 'david.gomez@email.com', 'Cra 70 # 32-15, Medellín'),
(3, '1040506070', 'Pedro Infante', '3151122334', 'pedro.infante@email.com', 'Av. El Poblado # 10-50, Medellín'),
(4, '1050607080', 'Camila Restrepo', '3005544332', 'camila.restrepo@email.com', 'Circular 4 # 73-10, Medellín'),
(5, '1060708090', 'Andrés Felipe Morales', '3206677889', 'andres.morales@email.com', 'Calle 10 # 30-22, Medellín');

-- Vehículos registrados
INSERT OR IGNORE INTO vehiculo (placa, tipo_vehiculo, marca, modelo, color, propietario_id, activo) VALUES
('ABC123', 'CARRO', 'Renault', 'Duster Intens 2.0', 'Gris Plata', 1, 1),
('MOT808', 'MOTO', 'Yamaha', 'NMAX 155 Connected', 'Azul Mate', 2, 1),
('XYZ999', 'CARRO', 'Chevrolet', 'Onix Turbo Sedán', 'Rojo Carmesí', 3, 1),
('MOT101', 'MOTO', 'Bajaj', 'Pulsar NS 200', 'Negro Nebulosa', 3, 1),
('KLR500', 'MOTO', 'Kawasaki', 'KLR 650 Adventure', 'Verde Militar', 4, 1),
('TOY456', 'CARRO', 'Toyota', 'Corolla Cross Híbrido', 'Blanco Perlado', 5, 1);

-- Mensualidades registradas
INSERT OR IGNORE INTO mensualidad (id, vehiculo_placa, fecha_pago, fecha_vencimiento, valor_pagado, estado) VALUES
(1, 'ABC123', date('now', '-10 days'), date('now', '+20 days'), 250000.00, 'ACTIVA'),
(2, 'MOT808', date('now', '-5 days'), date('now', '+25 days'), 100000.00, 'ACTIVA'),
(3, 'XYZ999', date('now', '-45 days'), date('now', '-15 days'), 250000.00, 'VENCIDA'),
(4, 'MOT101', date('now', '-40 days'), date('now', '-10 days'), 100000.00, 'VENCIDA'),
(5, 'KLR500', date('now', '-2 days'), date('now', '+28 days'), 100000.00, 'ACTIVA'),
(6, 'TOY456', date('now', '-12 days'), date('now', '+18 days'), 250000.00, 'ACTIVA');

-- Historial semilla de pagos (Iteración 3 - Coherente con las mensualidades base)
INSERT OR IGNORE INTO pago (id, numero_recibo, vehiculo_placa, mensualidad_id, fecha_pago, periodo_inicio, periodo_fin, meses_pagados, valor_pagado, metodo_pago, referencia_comprobante, tipo_aplicacion, estado, observaciones, usuario_id) VALUES
(1, 'REC-SEED-0001', 'ABC123', 1, date('now', '-10 days'), date('now', '-10 days'), date('now', '+20 days'), 1, 250000.00, 'TRANSFERENCIA_BANCARIA', 'BANCOL-88210', 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Pago mensualidad inicial en plataforma', 2),
(2, 'REC-SEED-0002', 'MOT808', 2, date('now', '-5 days'), date('now', '-5 days'), date('now', '+25 days'), 1, 100000.00, 'CODIGO_QR', 'QR-77412', 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Pago con código QR en cabina norte', 2),
(3, 'REC-SEED-0003', 'XYZ999', 3, date('now', '-45 days'), date('now', '-45 days'), date('now', '-15 days'), 1, 250000.00, 'EFECTIVO', 'CAJA-0019', 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Mensualidad anterior (hoy vencida hace 15 días)', 3),
(4, 'REC-SEED-0004', 'MOT101', 4, date('now', '-40 days'), date('now', '-40 days'), date('now', '-10 days'), 1, 100000.00, 'EFECTIVO', 'CAJA-0024', 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Mensualidad anterior (hoy vencida hace 10 días)', 3),
(5, 'REC-SEED-0005', 'KLR500', 5, date('now', '-2 days'), date('now', '-2 days'), date('now', '+28 days'), 1, 100000.00, 'CONSIGNACION', 'CONS-55019', 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Consignación bancaria verificada en recibo', 2),
(6, 'REC-SEED-0006', 'TOY456', 6, date('now', '-12 days'), date('now', '-12 days'), date('now', '+18 days'), 1, 250000.00, 'CODIGO_QR', 'QR-99104', 'INICIAL_REACTIVACION', 'CONFIRMADO', 'Pago QR verificado por administrador', 1);
