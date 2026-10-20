"""
Módulo de Gestión de Base de Datos - Autos Colombia 24/7
Iteración 1: Entrada y Salida de Vehículos
Docente: Reinaldo Rojas
"""

import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autos_colombia.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database_schema.sql")

def get_connection():
    """Obtiene una conexión SQLite configurada con row_factory como dict."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_base_datos():
    """Ejecuta el script DDL/DML inicial si la base de datos no existe o está vacía."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si la tabla celda ya existe y tiene las 80 celdas
    cursor.execute("SELECT count(*) as total FROM sqlite_master WHERE type='table' AND name='celda';")
    existe = cursor.fetchone()['total']
    
    if existe:
        cursor.execute("SELECT count(*) as total FROM celda;")
        total_celdas = cursor.fetchone()['total']
        if total_celdas >= 80:
            conn.close()
            return

    # Si no existe o no tiene las 80 celdas, ejecutar el schema completo
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Base de datos 'autos_colombia.db' inicializada exitosamente con 80 celdas.")

if __name__ == "__main__":
    inicializar_base_datos()
