import sqlite3
from typing import Any

DB_NAME = "products.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_table() -> None:
    query = """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL CHECK(length(trim(name)) > 0),
        price REAL NOT NULL CHECK(price >= 0),
        stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
        category TEXT NOT NULL CHECK(length(trim(category)) > 0),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
    with get_connection() as conn:
        conn.execute(query)
        conn.commit()

def drop_table_products() -> None:
    query = """
    DROP TABLE products
    """
    with get_connection() as conn:
        conn.execute(query)
        conn.commit()
    create_table()

def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)

# POST
def insert_product(name: str, price: float, stock: int, category: str) -> int:
    query = """
    INSERT INTO products (name, price, stock, category)
    VALUES (?, ?, ?, ?)
    """

    # use this always to make sure the connection was closed after usage (also if error occured)
    with get_connection() as conn:
        conn = get_connection()
        cursor = conn.execute(query, (name, price, stock, category))
        conn.commit()
        return cursor.lastrowid  #  get the id of the row (product) that was just created

    # what does with do?
    # explanation
    # try:
    #     conn = get_connection()
    #     conn.commit()
    #     return cursor.lastrowid
    # finally:
    #     conn.close()

# GET
def get_all_products() -> list[dict[str, Any]]:
    query = "SELECT * FROM products ORDER BY id"
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        return [row_to_dict(row) for row in rows]


# GET/{id}
def get_product_by_id(product_id: int) -> dict[str, Any] | None:
    query = "SELECT * FROM products WHERE id = ?"
    with get_connection() as conn:
        row = conn.execute(query, (product_id,)).fetchone()
        return row_to_dict(row) if row else None


# PUT/{id} or PATCH/{id}
def update_product(product_id: int, name: str, price: float, stock: int, category: str) -> bool:
    query = """
    UPDATE products
    SET name = ?, price = ?, stock = ?, category = ?
    WHERE id = ?
    """
    with get_connection() as conn:
        cursor = conn.execute(query, (name, price, stock, category, product_id))
        conn.commit()
        return cursor.rowcount > 0

# DEl
def delete_product(product_id: int) -> bool:
    query = "DELETE FROM products WHERE id = ?"
    with get_connection() as conn:
        cursor = conn.execute(query, (product_id,))
        conn.commit()
        return cursor.rowcount > 0


create_table()