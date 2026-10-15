import sqlite3
import hashlib


# ==================================================
# DATABASE SETUP
# ==================================================

def create_users_table():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ==================================================
# PASSWORD HASHING
# ==================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ==================================================
# REGISTER USER
# ==================================================

def register_user(username, password):

    create_users_table()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:

        cursor.execute("""
        INSERT INTO users
        (username, password)
        VALUES (?, ?)
        """, (
            username,
            hashed_password
        ))

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:

        conn.close()

        return False


# ==================================================
# LOGIN USER
# ==================================================

def login_user(username, password):

    create_users_table()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
    SELECT id, username
    FROM users
    WHERE username = ?
    AND password = ?
    """, (
        username,
        hashed_password
    ))

    user = cursor.fetchone()

    conn.close()

    return user