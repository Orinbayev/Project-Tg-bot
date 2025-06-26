import sqlite3
from datetime import datetime

# Database filename
movie_db = "kinoo.db"

# --- MOVIE SECTION ---

def init_kino_db():
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                code INTEGER PRIMARY KEY,
                caption TEXT,
                info TEXT,
                link TEXT
            )
        """)
        conn.commit()

# Add a new movie entry
def add_movie(code: int, caption: str, info: str, link: str):
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO movies (code, caption, info, link)
            VALUES (?, ?, ?, ?)
        """, (code, caption, info, link))
        conn.commit()

# Get all movies
def read_db():
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code, caption, info, link FROM movies")
        return cursor.fetchall()

# Delete movie
def delete_movie(code: int) -> bool:
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE code = ?", (code,))
        conn.commit()
        return cursor.rowcount > 0

# Update movie
def update_movie(code: int, new_caption: str, new_info: str, new_link: str) -> bool:
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE movies
            SET caption = ?, info = ?, link = ?
            WHERE code = ?
        """, (new_caption, new_info, new_link, code))
        conn.commit()
        return cursor.rowcount > 0

# --- USERS SECTION ---

def init_users_table():
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_at TEXT
            )
        """)
        conn.commit()

def add_user(user_id: int):
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, joined_at)
            VALUES (?, ?)
        """, (user_id, datetime.now().isoformat()))
        conn.commit()

def get_all_users():
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in cursor.fetchall()]

def get_total_users():
    with sqlite3.connect(movie_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]