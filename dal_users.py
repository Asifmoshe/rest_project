import sqlite3
from passlib.context import CryptContext
import hashlib

"""
Data access layer for user management.

This module handles all database operations related to users, including table
creation, user CRUD actions, password hashing, and login validation.
"""

import hashlib
import sqlite3
from typing import Any

from passlib.context import CryptContext

DB_NAME = "users.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_connection() -> sqlite3.Connection:
    """
    Create a SQLite connection configured to return rows as dictionaries.

    Returns:
        sqlite3.Connection: Open connection to the users database.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """
    Convert a SQLite row object into a plain dictionary.

    Args:
        row (sqlite3.Row | None): Row fetched from the database.

    Returns:
        dict[str, Any] | None: Converted dictionary or None if no row exists.
    """
    if row is None:
        return None
    return dict(row)


def hash_password(password: str) -> str:
    """
    Hash a password before storing it in the database.

    The password is first hashed with SHA-256 and then hashed again using bcrypt
    through Passlib.

    Args:
        password (str): Plain-text password.

    Returns:
        str: Secure hashed password.
    """
    sha_password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against the stored hash.

    Args:
        plain_password (str): Password provided by the user.
        hashed_password (str): Stored password hash from the database.

    Returns:
        bool: True if the password matches, otherwise False.
    """
    sha_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(sha_password, hashed_password)


def create_table_users() -> None:
    """
    Create the users table if it does not already exist.
    """
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


def drop_table_users() -> None:
    """
    Drop the users table if it exists.
    """
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS users")


def recreate_table_users() -> None:
    """
    Recreate the users table from scratch.

    Useful for testing or resetting the database.
    """
    drop_table_users()
    create_table_users()


def get_all_users() -> list[dict[str, Any]]:
    """
    Fetch all users from the database.

    Returns:
        list[dict[str, Any]]: List of user records ordered by id.
    """
    query = """
    SELECT id, user_name, email, created_at
    FROM users
    ORDER BY id
    """
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return [row_to_dict(row) for row in rows]


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """
    Fetch a single user by database id.

    Args:
        user_id (int): User id.

    Returns:
        dict[str, Any] | None: User record or None if not found.
    """
    query = """
    SELECT id, user_name, email, created_at
    FROM users
    WHERE id = ?
    """
    with get_connection() as conn:
        row = conn.execute(query, (user_id,)).fetchone()
    return row_to_dict(row)


def get_user_by_username(user_name: str) -> dict[str, Any] | None:
    """
    Fetch a single user by username.

    Args:
        user_name (str): Username to search for.

    Returns:
        dict[str, Any] | None: Full user record or None if not found.
    """
    query = "SELECT * FROM users WHERE user_name = ?"
    with get_connection() as conn:
        row = conn.execute(query, (user_name,)).fetchone()
    return row_to_dict(row)


def insert_user(user_name: str, email: str, password: str) -> dict[str, Any] | None:
    """
    Insert a new user into the database.

    Args:
        user_name (str): Desired username.
        email (str): User email.
        password (str): Plain-text password.

    Returns:
        dict[str, Any] | None: Newly created user record, or None if username or
        email already exists.
    """
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


def update_user(
    user_id: int,
    user_name: str,
    email: str,
    password: str,
) -> dict[str, Any] | str | None:
    """
    Update an existing user's details.

    Args:
        user_id (int): User id to update.
        user_name (str): New username.
        email (str): New email.
        password (str): New plain-text password.

    Returns:
        dict[str, Any] | str | None:
            - Updated user record on success
            - "duplicate" if username or email already exists
            - None if the user does not exist
    """
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
                (user_name, email, hashed_password, user_id),
            )
            affected_rows = cursor.rowcount

        if affected_rows == 0:
            return None

        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return "duplicate"


def delete_user(user_id: int) -> dict[str, Any] | None:
    """
    Delete a user from the database.

    Args:
        user_id (int): User id to delete.

    Returns:
        dict[str, Any] | None: Deleted user record, or None if not found.
    """
    existing_user = get_user_by_id(user_id)
    if existing_user is None:
        return None

    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return existing_user


def login_user(user_name: str, password: str) -> bool:
    """
    Validate username and password for login.

    Args:
        user_name (str): Username supplied by the client.
        password (str): Plain-text password supplied by the client.

    Returns:
        bool: True if the login credentials are valid, otherwise False.
    """
    user = get_user_by_username(user_name)
    if user is None:
        return False

    return verify_password(password, user["password"])