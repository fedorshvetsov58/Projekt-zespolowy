import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    script_path = os.path.join(os.path.dirname(__file__), 'models.sql')
    with open(script_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
