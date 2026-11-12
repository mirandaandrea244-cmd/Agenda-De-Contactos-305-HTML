import sqlite3


def obtener_conexion():
    # Abre la base de datos. Si no existe, SQLite la crea.
    conexion = sqlite3.connect("contactos.db")
    # Permite acceder a las columnas por su nombre.
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tabla():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT,
            categoria TEXT NOT NULL,
            foto TEXT
        )
    """)
    # Si la tabla ya existía sin la columna foto, la agregamos.
    columnas = [f["name"] for f in cursor.execute("PRAGMA table_info(contactos)").fetchall()]
    if "foto" not in columnas:
        cursor.execute("ALTER TABLE contactos ADD COLUMN foto TEXT")
    conexion.commit()
    conexion.close()