import sqlite3
from datetime import datetime, timedelta

DB_NAME = "users.db"

def init_users_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_seen TIMESTAMP,
                last_active TIMESTAMP
            )
        """)
        conn.commit()

def register_user(user_id: int):
    now = datetime.utcnow()
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if c.fetchone():
            c.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
        else:
            c.execute("INSERT INTO users (user_id, first_seen, last_active) VALUES (?, ?, ?)", (user_id, now, now))
        conn.commit()

def get_total_users():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        return c.fetchone()[0]

def get_new_users_in_last_24h():
    since = datetime.utcnow() - timedelta(hours=24)
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE first_seen >= ?", (since,))
        return c.fetchone()[0]

def get_new_users_in_last_30d():
    since = datetime.utcnow() - timedelta(days=30)
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE first_seen >= ?", (since,))
        return c.fetchone()[0]

def get_active_users_in_last_7d():
    since = datetime.utcnow() - timedelta(days=7)
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE last_active >= ?", (since,))
        return c.fetchone()[0]

def get_all_user_ids():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        return [row[0] for row in c.fetchall()]

