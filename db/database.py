
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "meals.sqlite3"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        full_name TEXT,
        verified INTEGER DEFAULT 0
    );""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        class_label TEXT NOT NULL,
        FOREIGN KEY(parent_id) REFERENCES parents(id)
    );""")
    conn.commit()
    conn.close()

def upsert_parent(tg_id: int):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO parents (tg_id) VALUES (?)", (tg_id,))
    conn.commit()
    conn.close()

def set_parent_name_and_verify(tg_id: int, full_name: str, verified: int = 1):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO parents (tg_id, full_name, verified) VALUES (?, ?, ?)", (tg_id, full_name, verified))
    c.execute("UPDATE parents SET full_name=?, verified=? WHERE tg_id=?", (full_name, verified, tg_id))
    conn.commit()
    conn.close()

def get_parent(tg_id: int):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM parents WHERE tg_id=?", (tg_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_child(parent_id: int, full_name: str, class_label: str):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO children (parent_id, full_name, class_label) VALUES (?, ?, ?)", (parent_id, full_name, class_label))
    conn.commit()
    conn.close()

def get_parent_children(parent_id: int):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM children WHERE parent_id=? ORDER BY id DESC", (parent_id,))
    rows = c.fetchall()
    conn.close()
    return rows
