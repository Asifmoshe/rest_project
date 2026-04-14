"""
Data access layer for user management.

This module contains all direct SQLite operations for the users table,
including table creation, CRUD actions, password hashing, and login
validation. Router modules should call these functions instead of writing SQL
queries directly.
"""

import hashlib
import sqlite3
from typing import Any

from passlib.context import CryptContext


DB_NAME = "users.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_connection() -> sqlite3.Connection:
    """
    Open a SQLite connection configured to return rows as dictionary-like rows.

    Returns:
        sqlite3.Connection: Open connection to the project database.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """
    Convert a SQLite row object into a plain Python dictionary.

    Args:
        row: Row returned from SQLite, or ``None`` when no row was found.

    Returns:
        dict[str, Any] | None: Converted row dictionary, or ``None``.
    """
    if row is None:
        return None
    return dict(row)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password before storing it in the database.

    The function first applies SHA-256 and then hashes the result with bcrypt
    through Passlib. This prevents storing the original password as plain text.

    Args:
        password: Plain-text password supplied by the user.

    Returns:
        str: Secure hash that can be safely stored in the database.
    """
    sha_password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether a plain-text password matches the stored password hash.

    Args:
        plain_password: Password supplied during login.
        hashed_password: Password hash stored in the database.

    Returns:
        bool: ``True`` if the password is valid, otherwise ``False``.
    """
    sha_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(sha_password, hashed_password)


def create_table_users() -> None:
    """
    Create the users table if it does not already exist.

    The table stores an id, username, email, encrypted password, and creation
    timestamp for each user.
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

    This function is intended mainly for local testing or resetting the
    project database.
    """
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS users")


def recreate_table_users() -> None:
    """
    Recreate the users table from scratch.

    Warning:
        Existing user records will be deleted.
    """
    drop_table_users()
    create_table_users()


def get_all_users() -> list[dict[str, Any]]:
    """
    Fetch all users without returning their password hashes.

    Returns:
        list[dict[str, Any]]: User records ordered by id.
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
    Fetch a single user by database id without returning the password hash.

    Args:
        user_id: User id to search for.

    Returns:
        dict[str, Any] | None: User record if found, otherwise ``None``.
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

    This function returns the full database row, including the password hash,
    because authentication needs the hash to validate login attempts.

    Args:
        user_name: Username to search for.

    Returns:
        dict[str, Any] | None: Full user record if found, otherwise ``None``.
    """
    query = "SELECT * FROM users WHERE user_name = ?"
    with get_connection() as conn:
        row = conn.execute(query, (user_name,)).fetchone()
    return row_to_dict(row)


def insert_user(user_name: str, email: str, password: str) -> dict[str, Any] | None:
    """
    Insert a new user into the database.

    Args:
        user_name: Desired username.
        email: User email address.
        password: Plain-text password that will be hashed before saving.

    Returns:
        dict[str, Any] | None: Created user record, or ``None`` if the username
        or email already exists.
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
    Update an existing user's username, email, and password.

    Args:
        user_id: Id of the user to update.
        user_name: New username.
        email: New email address.
        password: New plain-text password that will be hashed before saving.

    Returns:
        dict[str, Any] | str | None: Updated user record on success,
        ``"duplicate"`` if the username or email already exists, or ``None``
        if the user id was not found.
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
    Delete a user from the database by id.

    Args:
        user_id: Id of the user to delete.

    Returns:
        dict[str, Any] | None: Deleted user record if it existed, otherwise
        ``None``.
    """
    existing_user = get_user_by_id(user_id)
    if existing_user is None:
        return None

    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return existing_user


def login_user(user_name: str, password: str) -> bool:
    """
    Validate login credentials.

    Args:
        user_name: Username supplied by the client.
        password: Plain-text password supplied by the client.

    Returns:
        bool: ``True`` when the username exists and the password matches,
        otherwise ``False``.
    """
    user = get_user_by_username(user_name)
    if user is None:
        return False
    return verify_password(password, user["password"])