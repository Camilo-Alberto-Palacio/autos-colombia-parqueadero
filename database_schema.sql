-- ====================================================================
-- PARQUEADERO AUTOS COLOMBIA 24/7 - SISTEMA DE CONTROL DE ACCESO
-- MODELO FÍSICO DE BASE DE DATOS (DDL & DML) - ITERACIÓN 1
-- Docente: Reinaldo Rojas
-- Reglas de Negocio:
--   - 80 Celdas: 10 Motos (M-01 a M-10), 70 Carros (C-01 a C-70)
--   - Modalidad exclusiva: Mensualidad ($250.000 Carro, $100.000 Moto)
--   - Asignación dinámica/aleatoria de celda según tipo de vehículo
--   - Validación estricta de mensualidad vigente y capacidad
-- ====================================================================

-- 1. TABLA: PROPIETARIO / CLIENTE ABONADO
CREATE TABLE IF NOT EXISTS propietario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento VARCHAR(20) NOT NULL UNIQUE,
    nombre_completo VARCHAR(120) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: VEHICULO
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

-- 3. TABLA: MENSUALIDAD (Cobro por vehículo)
CREATE TABLE IF NOT EXISTS mensualidad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_placa VARCHAR(10) NOT NULL,
    fecha_pago DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    valor_pagado DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(15) NOT NULL CHECK (estado IN ('ACTIVA', 'VENCIDA', 'CANCELADA')),
    FOREIGN KEY (vehiculo_placa) REFERENCES vehiculo(placa) ON DELETE CASCADE
);

-- 4. TABLA: CELDA (Exactamente 80 celdas fijas)
CREATE TABLE IF NOT EXISTS celda (
    codigo VARCHAR(10) PRIMARY KEY,
    tipo_permitido VARCHAR(10) NOT NULL CHECK (tipo_permitido IN ('CARRO', 'MOTO')),
    estado VARCHAR(15) NOT NULL DEFAULT 'DISPONIBLE' CHECK (estado IN ('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO')),
    piso INTEGER DEFAULT 1,
    zona VARCHAR(20) DEFAULT 'PRINCIPAL'
);

-- 5. TABLA: REGISTRO_ACCESO (Control de Entrada y Salida 24/7)
CREATE TABLE IF NOT EXISTS registro_acceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_placa VARCHAR(10) NOT NULL,
    celda_codigo VARCHAR(10) NOT NULL,
    fecha_ingreso DATETIME NOT NULL,
    fecha_salida DATETIME,
    estado VARCHAR(15) NOT NULL DEFAULT 'ADENTRO' CHECK (estado IN ('ADENTRO', 'FINALIZADO')),
    observaciones TEXT,
    FOREIGN KEY (vehiculo_placa) REFERENCES vehiculo(placa) ON DELETE RESTRICT,
    FOREIGN KEY (celda_codigo) REFERENCES celda(codigo) ON DELETE RESTRICT
);

-- ÍNDICES PARA ALTO RENDIMIENTO EN BÚSQUEDAS
CREATE INDEX IF NOT EXISTS idx_vehiculo_placa ON vehiculo(placa);
CREATE INDEX IF NOT EXISTS idx_celda_estado_tipo ON celda(tipo_permitido, estado);
CREATE INDEX IF NOT EXISTS idx_registro_activo ON registro_acceso(vehiculo_placa, estado);
CREATE INDEX IF NOT EXISTS idx_mensualidad_placa ON mensualidad(vehiculo_placa, fecha_vencimiento);

-- ====================================================================
-- INSERCIÓN DE DATOS SEMILLA (80 CELDAS REGLAMENTARIAS)
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

-- ====================================================================
-- CLIENTES Y VEHÍCULOS DE PRUEBA PARA VALIDACIÓN DOCENTE
-- ====================================================================

-- Propietarios de prueba
INSERT OR IGNORE INTO propietario (id, documento, nombre_completo, telefono, email) VALUES
(1, '1020304050', 'Juan Carlos Pérez', '3104567890', 'juan.perez@email.com'),
(2, '1030405060', 'David Gómez', '3129876543', 'david.gomez@email.com'),
(3, '1040506070', 'Pedro Infante', '3151122334', 'pedro.infante@email.com'),
(4, '1050607080', 'Camila Restrepo', '3005544332', 'camila.restrepo@email.com'),
(5, '1060708090', 'Andrés Felipe Morales', '3206677889', 'andres.morales@email.com');

-- Vehículos registrados
-- ABC123: Carro con mensualidad vigente (Al día)
-- MOT808: Moto con mensualidad vigente (Al día)
-- XYZ999: Carro con mensualidad VENCIDA (Para probar denegación)
-- MOT101: Moto con mensualidad VENCIDA (Para probar denegación)
-- KLR500: Moto con mensualidad vigente (Al día)
-- TOY456: Carro con mensualidad vigente (Al día)
INSERT OR IGNORE INTO vehiculo (placa, tipo_vehiculo, marca, modelo, color, propietario_id, activo) VALUES
('ABC123', 'CARRO', 'Renault', 'Duster Intens 2.0', 'Gris Plata', 1, 1),
('MOT808', 'MOTO', 'Yamaha', 'NMAX 155 Connected', 'Azul Mate', 2, 1),
('XYZ999', 'CARRO', 'Chevrolet', 'Onix Turbo Sedán', 'Rojo Carmesí', 3, 1),
('MOT101', 'MOTO', 'Bajaj', 'Pulsar NS 200', 'Negro Nebulosa', 3, 1),
('KLR500', 'MOTO', 'Kawasaki', 'KLR 650 Adventure', 'Verde Militar', 4, 1),
('TOY456', 'CARRO', 'Toyota', 'Corolla Cross Híbrido', 'Blanco Perlado', 5, 1);

-- Mensualidades registradas (Tarifas oficiales: $250.000 Carro, $100.000 Moto)
-- ABC123: Vigente hasta dentro de 20 días
INSERT OR IGNORE INTO mensualidad (vehiculo_placa, fecha_pago, fecha_vencimiento, valor_pagado, estado) VALUES
('ABC123', date('now', '-10 days'), date('now', '+20 days'), 250000.00, 'ACTIVA'),
('MOT808', date('now', '-5 days'), date('now', '+25 days'), 100000.00, 'ACTIVA'),
('XYZ999', date('now', '-45 days'), date('now', '-15 days'), 250000.00, 'VENCIDA'),
('MOT101', date('now', '-40 days'), date('now', '-10 days'), 100000.00, 'VENCIDA'),
('KLR500', date('now', '-2 days'), date('now', '+28 days'), 100000.00, 'ACTIVA'),
('TOY456', date('now', '-12 days'), date('now', '+18 days'), 250000.00, 'ACTIVA');
