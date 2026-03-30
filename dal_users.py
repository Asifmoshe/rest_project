import sqlite3
from passlib.context import CryptContext
import hashlib

DB_NAME = "users.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def hash_password(password: str):
    # Step 1: hash with SHA256 (no length limit)
    sha_password = hashlib.sha256(password.encode()).hexdigest()

    # Step 2: bcrypt the result
    return pwd_context.hash(sha_password)


def verify_password(plain_password: str, hashed_password: str):
    sha_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(sha_password, hashed_password)


def create_table_users():
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    with get_connection() as conn:
        conn.execute(query)


def drop_table_users():
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS users")


def recreate_table_users():
    drop_table_users()
    create_table_users()

###### GET action ######
def get_all_users():
    query = """
    SELECT id, user_name, email, created_at
    FROM users
    ORDER BY id
    """
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return [row_to_dict(row) for row in rows]

###### GET-BY-ID action ######
def get_user_by_id(user_id):
    query = """
    SELECT id, user_name, email, created_at
    FROM users
    WHERE id = ?
    """
    with get_connection() as conn:
        row = conn.execute(query, (user_id,)).fetchone()
    return row_to_dict(row)

###### GET action ######
def get_user_by_username(user_name):
    query = """
    SELECT *
    FROM users
    WHERE user_name = ?
    """
    with get_connection() as conn:
        row = conn.execute(query, (user_name,)).fetchone()
    return row_to_dict(row)

###### POST action ######
def insert_user(user_name, email, password):
    query = """
    INSERT INTO users (user_name, email, password)
    VALUES (?, ?, ?)
    """
    hashed_password = hash_password(password)

    try:
        with get_connection() as conn:
            cursor = conn.execute(query, (user_name, email, hashed_password))
            user_id = cursor.lastrowid
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None

###### PUT action ######
def update_user(user_id, user_name, email, password):
    query = """
    UPDATE users
    SET user_name = ?, email = ?, password = ?
    WHERE id = ?
    """
    hashed_password = hash_password(password)

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (user_name, email, hashed_password, user_id)
            )
            affected_rows = cursor.rowcount

        if affected_rows == 0:
            return None

        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return "duplicate"

###### DELETE action ######
def delete_user(user_id):
    existing_user = get_user_by_id(user_id)
    if existing_user is None:
        return None

    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return existing_user


def login_user(user_name, password):
    user = get_user_by_username(user_name)

    if user is None:
        return False

    return verify_password(password, user["password"])