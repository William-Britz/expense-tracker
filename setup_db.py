# setup_db.py
# Author  : William
# Version : 1.0
#
# Run this script once to initialise the database.
# Run it again any time you need to reset to a clean state.
# WARNING: running it again drops and recreates the database entirely.

import os
import bcrypt
from database.db_connect import get_connection, DB_PATH


def create_tables():
    schema_path = os.path.join(
        os.path.dirname(__file__), 'database', 'schema.sql'
    )
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn = get_connection()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Tables created.")


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Default categories
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

    # Default admin account — change this password after first login
    admin_password = bcrypt.hashpw(
        'admin123'.encode(), bcrypt.gensalt()
    ).decode()
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password_hash, role) '
        'VALUES (?, ?, ?)',
        ('admin', admin_password, 'admin')
    )

    # Default standard user account
    user_password = bcrypt.hashpw(
        'user123'.encode(), bcrypt.gensalt()
    ).decode()
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password_hash, role) '
        'VALUES (?, ?, ?)',
        ('demo_user', user_password, 'user')
    )

    conn.commit()
    conn.close()
    print("Seed data inserted.")
    print("Admin login  : username=admin      password=admin123")
    print("Demo login   : username=demo_user  password=user123")


if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database removed.")
    create_tables()
    seed_data()
    print(f"Database created at: {DB_PATH}")