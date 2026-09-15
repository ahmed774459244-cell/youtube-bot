"""
Foydalanuvchilarning video-daqiqa balansini va to'lov so'rovlarini SQLite'da saqlaydi.
Qo'shimcha kutubxona talab qilmaydi (Python bilan birga keladigan sqlite3 ishlatiladi).
"""
import sqlite3
import threading
import time

DB_PATH = "bot_database.db"
_lock = threading.Lock()


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with _lock:
        conn = _get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance_minutes REAL NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                package_id TEXT NOT NULL,
                minutes REAL NOT NULL,
                price INTEGER NOT NULL,
                photo_file_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS click_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_trans_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                package_id TEXT NOT NULL,
                minutes REAL NOT NULL,
                amount INTEGER NOT NULL,
                click_trans_id TEXT,
                status TEXT NOT NULL DEFAULT 'created',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sms_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                minutes REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()


def get_or_create_user(user_id: int, free_minutes: float) -> float:
    """Foydalanuvchini bazadan topadi, topilmasa yaratadi (bepul daqiqalar bilan). Balansni qaytaradi."""
    with _lock:
        conn = _get_conn()
        cur = conn.execute("SELECT balance_minutes FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO users (user_id, balance_minutes) VALUES (?, ?)",
                (user_id, free_minutes),
            )
            conn.commit()
            balance = free_minutes
        else:
            balance = row[0]
        conn.close()
        return balance


def get_balance(user_id: int) -> float:
    with _lock:
        conn = _get_conn()
        cur = conn.execute("SELECT balance_minutes FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0.0


def deduct_balance(user_id: int, minutes: float):
    with _lock:
        conn = _get_conn()
        conn.execute(
            "UPDATE users SET balance_minutes = balance_minutes - ? WHERE user_id=?",
            (minutes, user_id),
        )
        conn.commit()
        conn.close()


def add_balance(user_id: int, minutes: float):
    with _lock:
        conn = _get_conn()
        conn.execute(
            "UPDATE users SET balance_minutes = balance_minutes + ? WHERE user_id=?",
            (minutes, user_id),
        )
        conn.commit()
        conn.close()


# --- Qo'lda tasdiqlanadigan to'lovlar ---

def create_pending_payment(user_id: int, package_id: str, minutes: float, price: int, photo_file_id: str) -> int:
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "INSERT INTO pending_payments (user_id, package_id, minutes, price, photo_file_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, package_id, minutes, price, photo_file_id),
        )
        conn.commit()
        payment_id = cur.lastrowid
        conn.close()
        return payment_id


def get_pending_payment(payment_id: int):
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT id, user_id, package_id, minutes, price, status FROM pending_payments WHERE id=?",
            (payment_id,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "user_id": row[1], "package_id": row[2], "minutes": row[3], "price": row[4], "status": row[5]}


def set_payment_status(payment_id: int, status: str):
    with _lock:
        conn = _get_conn()
        conn.execute("UPDATE pending_payments SET status=? WHERE id=?", (status, payment_id))
        conn.commit()
        conn.close()


# --- Click.uz orqali avtomatik to'lovlar ---

def create_click_order(user_id: int, package_id: str, minutes: float, amount: int) -> str:
    """Yangi Click buyurtma yaratadi, noyob merchant_trans_id qaytaradi."""
    merchant_trans_id = f"{user_id}-{package_id}-{int(time.time())}"
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO click_orders (merchant_trans_id, user_id, package_id, minutes, amount) VALUES (?, ?, ?, ?, ?)",
            (merchant_trans_id, user_id, package_id, minutes, amount),
        )
        conn.commit()
        conn.close()
    return merchant_trans_id


def get_click_order(merchant_trans_id: str):
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT id, merchant_trans_id, user_id, package_id, minutes, amount, status FROM click_orders WHERE merchant_trans_id=?",
            (merchant_trans_id,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0], "merchant_trans_id": row[1], "user_id": row[2],
            "package_id": row[3], "minutes": row[4], "amount": row[5], "status": row[6],
        }


def mark_click_order_prepared(merchant_trans_id: str, click_trans_id: str):
    with _lock:
        conn = _get_conn()
        conn.execute(
            "UPDATE click_orders SET click_trans_id=?, status='prepared' WHERE merchant_trans_id=?",
            (click_trans_id, merchant_trans_id),
        )
        conn.commit()
        conn.close()


def mark_click_order_paid(merchant_trans_id: str):
    with _lock:
        conn = _get_conn()
        conn.execute(
            "UPDATE click_orders SET status='paid' WHERE merchant_trans_id=?",
            (merchant_trans_id,),
        )
        conn.commit()
        conn.close()


# --- SMS orqali avtomatik to'lovni aniqlash (Click shartnomasisiz) ---

def create_sms_order(user_id: int, amount: int, minutes: float) -> int:
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "INSERT INTO sms_orders (user_id, amount, minutes) VALUES (?, ?, ?)",
            (user_id, amount, minutes),
        )
        conn.commit()
        order_id = cur.lastrowid
        conn.close()
        return order_id


def find_matching_sms_order(amount: int, window_minutes: int):
    """Berilgan summaga mos, hali kutilayotgan (pending) va vaqt oynasi ichidagi eng eski buyurtmani topadi."""
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            """
            SELECT id, user_id, amount, minutes FROM sms_orders
            WHERE amount=? AND status='pending'
              AND datetime(created_at) >= datetime('now', ?)
            ORDER BY created_at ASC LIMIT 1
            """,
            (amount, f"-{window_minutes} minutes"),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "user_id": row[1], "amount": row[2], "minutes": row[3]}


def mark_sms_order_paid(order_id: int):
    with _lock:
        conn = _get_conn()
        conn.execute("UPDATE sms_orders SET status='paid' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()


def get_sms_order(order_id: int):
    with _lock:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT id, user_id, amount, minutes, status FROM sms_orders WHERE id=?", (order_id,)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "user_id": row[1], "amount": row[2], "minutes": row[3], "status": row[4]}
