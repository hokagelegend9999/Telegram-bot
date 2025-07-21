# /opt/hokage-bot/database.py

import logging
import datetime
import subprocess # Ditambahkan untuk memanggil script shell

logger = logging.getLogger(__name__)

# --- Dummy Database untuk Demonstrasi (Ganti dengan database nyata Anda) ---
# Ini hanya contoh sederhana untuk menyimpan data di memori
_users_db = {} # {user_id: {"first_name": "", "username": ""}}
_accounts_db = [] # [{"username": "", "type": "", "expiration_date": "", "user_id": ""}]
# --- Akhir Dummy Database ---


def init_db():
    """
    Fungsi ini harus berisi logika inisialisasi database nyata Anda.
    Contoh: koneksi ke SQLite, pembuatan tabel, dll.
    """
    logger.info("Database siap.")

    # --- Contoh dummy data untuk pengujian List Akun (HAPUS ATAU GANTI DENGAN LOGIKA DB NYATA) ---
    global _accounts_db # Agar bisa dimodifikasi
    global _users_db
    if not _accounts_db: # Hanya tambahkan dummy jika kosong
        _accounts_db.append({"username": "dummyuser1", "type": "SSH", "expiration_date": (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"), "user_id": 1469244768})
        _accounts_db.append({"username": "dummyuser2", "type": "SSH", "expiration_date": (datetime.date.today() + datetime.timedelta(days=60)).strftime("%Y-%m-%d"), "user_id": 1469244768})
        _accounts_db.append({"username": "dummyuser_vmess", "type": "VMESS", "expiration_date": (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d"), "user_id": 1469244768})
    if not _users_db: # Tambahkan dummy user jika kosong
        _users_db[1469244768] = {"first_name": "TestUser", "username": "test_username"}
    # --- Akhir Contoh dummy data ---

    # Contoh nyata (SQLite):
    # import sqlite3
    # conn = sqlite3.connect('bot_data.db')
    # cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS users (
    #         user_id INTEGER PRIMARY KEY,
    #         first_name TEXT,
    #         username TEXT
    #     )
    # ''')
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS accounts (
    #         username TEXT PRIMARY KEY,
    #         type TEXT,
    #         expiration_date TEXT,
    #         user_id INTEGER
    #     )
    # ''')
    # conn.commit()
    # conn.close()


def add_user_if_not_exists(user_id: int, first_name: str, username: str = None):
    """
    Menambahkan user ke database jika belum ada.
    Implementasikan logika DB nyata Anda di sini.
    """
    if user_id not in _users_db:
        _users_db[user_id] = {"first_name": first_name, "username": username}
        logger.info(f"User {user_id} ({username}) added to DB.")
        # Logika nyata: INSERT INTO users ...
    else:
        logger.info(f"User {user_id} ({username}) already exists in DB.")

async def renew_account(username: str, renew_type: str, user_id: int) -> bool:
    """
    Fungsi placeholder untuk memperpanjang akun di database atau melalui API.
    Anda perlu mengimplementasikan logika sebenarnya di sini.
    """
    logger.info(f"Attempting to renew account: {username} for type: {renew_type} by user {user_id}")

    try:
        # --- IMPLEMENTASI LOGIKA PERPANjangan NYATA ANDA DI SINI ---
        # Contoh:
        # 1. Query database Anda untuk menemukan akun berdasarkan username.
        # 2. Perbarui tanggal kedaluwarsa akun (misalnya, tambah 30 hari).
        # 3. Panggil API server SSH/VPN Anda untuk menerapkan perubahan.

        # Simulasi dummy:
        found = False
        for acc in _accounts_db:
            if acc["username"] == username and acc["user_id"] == user_id: # Contoh: hanya user pemilik yang bisa renew
                current_exp = datetime.datetime.strptime(acc["expiration_date"], "%Y-%m-%d")
                new_exp = current_exp + datetime.timedelta(days=30) # Perpanjang 30 hari
                acc["expiration_date"] = new_exp.strftime("%Y-%m-%d")
                logger.info(f"Dummy renewed {username} to {acc['expiration_date']}")
                found = True
                break

        if found:
            return True # Simulasi sukses
        else:
            return False # Akun tidak ditemukan atau bukan milik user

    except Exception as e:
        logger.error(f"Error in renew_account for {username}, type {renew_type}: {e}")
        return False

async def get_ssh_account_list(user_id: int) -> str:
    """
    Mengambil daftar akun SSH dari sistem/VPS nyata dengan memanggil script shell.
    """
    logger.info(f"Fetching SSH account list from system for user: {user_id}")

    try:
        # Panggil script shell 'list_ssh_users.sh' yang harus Anda buat
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/list_ssh_users.sh'], # Panggil script list user
            capture_output=True,
            text=True,
            check=True, # Akan raise CalledProcessError jika script gagal
            timeout=30 # Timeout 30 detik
        )

        output_lines = p.stdout.strip()

        if not output_lines or "Belum ada akun SSH yang ditemukan di sistem." in output_lines:
            return "Belum ada akun SSH yang terdaftar di VPS."

        return output_lines

    except subprocess.CalledProcessError as e:
        logger.error(f"Error calling list_ssh_users.sh: {e.stderr}", exc_info=True)
        return "❌ Gagal mengambil daftar akun: Error skrip. Hubungi admin."
    except Exception as e:
        logger.error(f"General error getting SSH account list: {e}", exc_info=True)
        return "❌ Terjadi kesalahan saat mengambil daftar akun. Coba lagi nanti."

async def get_vmess_account_list(user_id: int) -> str: # <--- FUNGSI BARU UNTUK VMESS LIST
    """
    Mengambil daftar akun VMESS dari sistem/VPS nyata dengan memanggil script shell.
    Anda perlu membuat list_vmess_users.sh
    """
    logger.info(f"Fetching VMESS account list from system for user: {user_id}")

    try:
        # Panggil script shell baru 'list_vmess_users.sh'
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/list_vmess_users.sh'], # Anda perlu membuat script ini
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        output_lines = p.stdout.strip()

        if not output_lines or "Belum ada akun VMESS yang ditemukan di sistem." in output_lines:
            return "Belum ada akun VMESS yang terdaftar di VPS."

        return output_lines

    except subprocess.CalledProcessError as e:
        logger.error(f"Error calling list_vmess_users.sh: {e.stderr}", exc_info=True)
        return "❌ Gagal mengambil daftar akun VMESS: Error skrip. Hubungi admin."
    except Exception as e:
        logger.error(f"General error getting VMESS account list: {e}", exc_info=True)
        return "❌ Terjadi kesalahan saat mengambil daftar akun VMESS. Coba lagi nanti."

# Fungsi placeholder untuk pembuatan akun SSH (Jika Anda mengelola di database)
async def create_ssh_account(username: str, password: str, duration: int, ip_limit: int, user_id: int) -> bool:
    logger.info(f"Simulating creation of SSH account for user {user_id}: {username}")
    # Tambahkan akun ke dummy db
    _accounts_db.append({
        "username": username,
        "type": "SSH",
        "expiration_date": (datetime.date.today() + datetime.timedelta(days=duration)).strftime("%Y-%m-%d"),
        "user_id": user_id
    })
    return True # Simulasi berhasil
