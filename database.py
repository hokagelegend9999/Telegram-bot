# Tambahkan fungsi ini di file database.py

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
