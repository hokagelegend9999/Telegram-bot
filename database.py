# database.py
import sqlite3
import logging
from datetime import datetime

DATABASE_FILE = "/opt/hokage-bot/hokage_store.db"

def get_db_connection():
    """Membuka koneksi ke database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        balance INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    logging.info("Database siap.")

def add_user_if_not_exists(telegram_id: int, first_name: str, username: str = None):
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    if not user:
        try:
            current_time = datetime.now()
            conn.execute(
                "INSERT INTO users (telegram_id, first_name, username, created_at) VALUES (?, ?, ?, ?)",
                (telegram_id, first_name, username, current_time)
            )
            conn.commit()
            logging.info(f"User baru ditambahkan: {first_name} (ID: {telegram_id})")
        except sqlite3.Error as e:
            logging.error(f"Gagal menambahkan user: {e}")
    conn.close()

def get_user(telegram_id: int):
    """Mengambil semua data user berdasarkan telegram_id."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    conn.close()
    return user

def get_all_users():
    """Mengambil semua user dari database."""
    conn = get_db_connection()
    users = conn.execute("SELECT telegram_id, first_name, username, role, balance FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return users

def update_balance(telegram_id: int, amount: int):
    """Menambah atau mengurangi saldo user. Gunakan nilai negatif untuk mengurangi."""
    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (amount, telegram_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Gagal update balance untuk {telegram_id}: {e}")
    finally:
        conn.close()
        
def update_role(telegram_id: int, new_role: str):
    """Mengubah peran (role) seorang user."""
    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET role = ? WHERE telegram_id = ?", (new_role, telegram_id))
        conn.commit()
        logging.info(f"Role untuk user {telegram_id} diubah menjadi {new_role}")
    except sqlite3.Error as e:
        logging.error(f"Gagal update role untuk {telegram_id}: {e}")
    finally:
        conn.close()
