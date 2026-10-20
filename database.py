"""
Módulo de Gestión de Base de Datos - Autos Colombia 24/7
Iteración 1: Entrada y Salida de Vehículos
Docente: Reinaldo Rojas
Soporte de Concurrencia Multi-Operario (WAL Mode + Transacciones Atómicas)
"""

import sqlite3
import os
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autos_colombia.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database_schema.sql")

# Lock de concurrencia para garantizar exclusión mutua entre múltiples operarios simultáneos
db_lock = threading.Lock()

def get_connection():
    """Obtiene una conexión SQLite configurada para concurrencia multi-hilo y claves foráneas."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def inicializar_base_datos():
    """Ejecuta el script DDL/DML inicial si la base de datos no existe o está vacía."""
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT count(*) as total FROM sqlite_master WHERE type='table' AND name='celda';")
        existe = cursor.fetchone()['total']
        
        if existe:
            cursor.execute("SELECT count(*) as total FROM celda;")
            total_celdas = cursor.fetchone()['total']
            if total_celdas >= 80:
                conn.close()
                return

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        print("Base de datos 'autos_colombia.db' inicializada exitosamente con 80 celdas (Modo WAL Concurrente).")

if __name__ == "__main__":
    inicializar_base_datos()
