# database/db_connect.py
# Author  : William
# Version : 1.0
#
# Single connection factory for the entire application.
# Every module that needs the database imports get_connection() from here.
# Never call sqlite3.connect() directly anywhere else in the codebase.

import sqlite3
import os

# Build the absolute path to the database file.
# BASE_DIR goes up one level from this file (database/) to the project root.
# This ensures the path works regardless of where Python is run from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'expensetracker.db')


def get_connection():
    """
    Returns an open SQLite connection with:
    - Foreign key enforcement enabled via PRAGMA foreign_keys = ON
    - row_factory set to sqlite3.Row so columns are accessible
      by name (row['amount']) instead of by index (row[3])

    Always call this function to get a connection.
    Never hardcode the database path anywhere else.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn