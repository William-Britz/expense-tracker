# setup_db.py
# Author  : William
# Version : 1.1
#
# Initialises the SQLite database for ExpenseTracker.
# Run once on first setup or any time a clean reset is needed.
# WARNING: re-running this script deletes all existing data.

import os
import sqlite3
import bcrypt
from database.db_connect import get_connection, DB_PATH


def create_tables() -> None:
    """
    Reads schema.sql and executes it against the database.
    Raises FileNotFoundError if the schema file is missing.
    Raises sqlite3.Error if any SQL statement fails.
    """
    schema_path = os.path.join(
        os.path.dirname(__file__), 'database', 'schema.sql'
    )

    if not os.path.exists(schema_path):
        raise FileNotFoundError(
            f"Schema file not found at: {schema_path}"
        )

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    conn = None
    try:
        conn = get_connection()
        conn.executescript(schema_sql)
        conn.commit()
        print("Tables created.")
    except sqlite3.Error as e:
        print(f"Database error during table creation: {e}")
        raise
    finally:
        if conn:
            conn.close()


def seed_data() -> None:
    """
    Inserts default categories and two seed user accounts.
    Uses INSERT OR IGNORE so re-running does not duplicate data.
    Passwords are bcrypt-hashed before storage.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Default expense categories
        categories = [
            ('Food & Groceries',  'Supermarkets, restaurants and takeaways'),
            ('Transport',         'Fuel, public transport and rideshare'),
            ('Housing',           'Rent, utilities and maintenance'),
            ('Entertainment',     'Streaming, events and hobbies'),
            ('Healthcare',        'Medical, pharmacy and gym'),
            ('Education',         'Courses, books and stationery'),
            ('Clothing',          'Clothes, shoes and accessories'),
            ('Other',             'Miscellaneous expenses'),
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)',
            categories
        )

        # Seed admin account
        admin_hash = bcrypt.hashpw(
            'admin123'.encode(), bcrypt.gensalt()
        ).decode()
        cursor.execute(
            'INSERT OR IGNORE INTO users (username, password_hash, role) '
            'VALUES (?, ?, ?)',
            ('admin', admin_hash, 'admin')
        )

        # Seed standard user account
        user_hash = bcrypt.hashpw(
            'user123'.encode(), bcrypt.gensalt()
        ).decode()
        cursor.execute(
            'INSERT OR IGNORE INTO users (username, password_hash, role) '
            'VALUES (?, ?, ?)',
            ('demo_user', user_hash, 'user')
        )

        conn.commit()
        print("Seed data inserted.")
        print("Default accounts ready. Change passwords after first login.")

    except sqlite3.Error as e:
        print(f"Database error during seeding: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database removed.")
    create_tables()
    seed_data()
    print(f"Database ready at: {DB_PATH}")