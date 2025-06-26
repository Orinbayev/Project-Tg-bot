import sqlite3

DB_NAME = "admin.db"

def init_admin_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY
            )
        """)

def add_admin(user_id: int) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
            return True
        except sqlite3.IntegrityError:
            return False

def remove_admin(user_id: int) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        return cur.rowcount > 0

def is_admin(user_id: int) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
        result = cur.fetchone() is not None
        print(f"🔍 Admin tekshirish: ID={user_id}, Natija={result}")
        return result

def get_all_admins():
    with sqlite3.connect(DB_NAME) as conn:
        return [row[0] for row in conn.execute("SELECT user_id FROM admins")]
