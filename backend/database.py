import sqlite3
from flask import g
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "studyq.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                topic TEXT NOT NULL,
                embedding BLOB NOT NULL,
                similar_ids TEXT DEFAULT '[]',
                agent_response TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        # Safe migration if table exists but without agent_response
        try:
            db.execute("ALTER TABLE questions ADD COLUMN agent_response TEXT;")
        except sqlite3.OperationalError:
            pass # Column likely exists
    print("Database initialised.")
