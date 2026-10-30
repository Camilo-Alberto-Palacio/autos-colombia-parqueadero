"""
Módulo de Gestión de Base de Datos - Autos Colombia 24/7
Iteración 1 y 2 Unificada: Entrada/Salida, Gestión de Usuarios (RBAC) y Gestión CRUD de Celdas
Asignatura: Ingeniería de Software - PREICA2602B020053
Docente: Reinaldo Rojas | Grupo: 25
Soporte de Concurrencia Multi-Operario (WAL Mode + Transacciones Atómicas + Migración Idempotente)
"""

import sqlite3
import os
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autos_colombia.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database_schema.sql")

# Lock de concurrencia para garantizar exclusión mutua entre múltiples operarios simultáneos
db_lock = threading.Lock()


def get_connection():
    """Obtiene una conexión SQLite configurada para concurrencia multi-hilo, integridad referencial y modo WAL."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def _columna_existe(cursor, tabla: str, columna: str) -> bool:
    """Verifica si una columna existe en una tabla SQLite dada."""
    cursor.execute(f"PRAGMA table_info({tabla});")
    columnas = [row["name"] for row in cursor.fetchall()]
    return columna in columnas


def inicializar_base_datos():
    """
    Inicializa o migra de forma idempotente el esquema físico de las Iteraciones 1 y 2.
    Garantiza que las 8 tablas normalizadas (3FN), índices, 80 celdas reglamentarias y
    usuarios semilla RBAC existan incluso si se ejecuta sobre una base de datos previa.
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # 1. Separar DDL (CREATE TABLE / CREATE INDEX) del DML semilla para migración limpia
        partes = schema_sql.split("-- DATOS SEMILLA:")
        ddl_sql = partes[0]
        cursor.executescript(ddl_sql)

        # 2. Migraciones defensivas sobre bases de datos creadas en la Iteración 1
        if not _columna_existe(cursor, "celda", "motivo_bloqueo"):
            cursor.execute("ALTER TABLE celda ADD COLUMN motivo_bloqueo TEXT;")
        if not _columna_existe(cursor, "registro_acceso", "usuario_id"):
            cursor.execute("ALTER TABLE registro_acceso ADD COLUMN usuario_id INTEGER REFERENCES usuario(id) ON DELETE SET NULL;")
        if not _columna_existe(cursor, "propietario", "direccion"):
            cursor.execute("ALTER TABLE propietario ADD COLUMN direccion VARCHAR(120);")

        # 3. Poblar datos semilla de forma idempotente (INSERT OR IGNORE) solo cuando falten registros base
        cursor.execute("SELECT count(*) AS total FROM celda;")
        total_celdas = cursor.fetchone()["total"]

        cursor.execute("SELECT count(*) AS total FROM usuario;")
        total_usuarios = cursor.fetchone()["total"]

        cursor.execute("SELECT count(*) AS total FROM vehiculo;")
        total_vehiculos = cursor.fetchone()["total"]

        if total_celdas < 80 or total_usuarios < 4 or total_vehiculos == 0:
            # Ejecutar el script completo con INSERT OR IGNORE sin duplicar mensualidades existentes
            if total_vehiculos > 0:
                # Si ya había vehículos y mensualidades, solo aseguramos celdas y usuarios semilla
                lineas_semilla = []
                en_mensualidad = False
                for linea in schema_sql.splitlines():
                    if linea.strip().startswith("-- Mensualidades registradas"):
                        en_mensualidad = True
                    if not en_mensualidad:
                        lineas_semilla.append(linea)
                cursor.executescript("\n".join(lineas_semilla))
            else:
                cursor.executescript(schema_sql)

        # Reparar hashes semilla heredados si existían con valores previos erróneos
        cursor.execute(
            "UPDATE usuario SET password_hash = ? WHERE username IN ('adriana_op', 'daniel_op') AND password_hash = ?",
            (
                "ea66d0295003394ff7f847590fe43af491ded28bb3837d543d55dfa130c9b2f3",
                "4c478e727de91ec0be54284bd97cf43666dca0df7cf542fb4fa996c5aa5a3c26",
            ),
        )
        cursor.execute(
            "UPDATE usuario SET password_hash = ? WHERE username = 'auditor' AND password_hash = ?",
            (
                "5b92db4dfb561dc69c949f34d36f5db0f8b30811be3a2949d85c5001279e9b1a",
                "c637a23c7f99996bb3caebdc698547b715a2eb41e42a98ef3879d924ae0c0e52",
            ),
        )

        conn.commit()
        conn.close()
        print("Base de datos 'autos_colombia.db' verificada e inicializada (Iteraciones 1 y 2 - Modo WAL Concurrente).")


if __name__ == "__main__":
    inicializar_base_datos()
