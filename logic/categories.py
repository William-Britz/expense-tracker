# logic/categories.py
# Author  : William
# Version : 1.0
#
# Category data operations for ExpenseTracker.
# Read access is available to all logged-in users.
# Write and delete operations are restricted to admin users only.

import sqlite3
from database.db_connect import get_connection
from logic.auth import is_admin


def get_all_categories() -> list:
    """
    Returns all categories ordered alphabetically.
    Available to all logged-in users — used to populate
    the category dropdown in the expense form.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, description FROM categories ORDER BY name'
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error in get_all_categories: {e}")
        return []
    finally:
        if conn:
            conn.close()


def add_category(name: str, description: str = '') -> dict:
    """
    Add a new expense category.
    Admin only — returns permission error for standard users.
    Returns a success/failure dict.
    """
    if not is_admin():
        return {'success': False, 'message': 'Admin access required.'}

    if not name or not name.strip():
        return {'success': False, 'message': 'Category name cannot be empty.'}

    conn = None
    try:
        conn = get_connection()
        conn.execute(
            'INSERT INTO categories (name, description) VALUES (?, ?)',
            (name.strip(), description.strip())
        )
        conn.commit()
        return {'success': True, 'message': f"Category '{name.strip()}' added."}
    except sqlite3.IntegrityError:
        # Triggered by the UNIQUE constraint on categories.name
        return {'success': False, 'message': f"Category '{name}' already exists."}
    except sqlite3.Error as e:
        return {'success': False, 'message': f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()


def delete_category(category_id: int) -> dict:
    """
    Delete a category by ID.
    Admin only — returns permission error for standard users.
    Will fail if expenses exist under this category due to the
    ON DELETE RESTRICT foreign key defined in the schema.
    Returns a success/failure dict.
    """
    if not is_admin():
        return {'success': False, 'message': 'Admin access required.'}

    conn = None
    try:
        conn = get_connection()
        conn.execute(
            'DELETE FROM categories WHERE id = ?',
            (category_id,)
        )
        conn.commit()
        return {'success': True, 'message': 'Category deleted.'}
    except sqlite3.IntegrityError:
        # ON DELETE RESTRICT fires when expenses reference this category
        return {
            'success': False,
            'message': 'Cannot delete: expenses exist under this category.'
        }
    except sqlite3.Error as e:
        return {'success': False, 'message': f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()


def get_category_by_id(category_id: int):
    """
    Returns a single category row by ID or None if not found.
    Used internally to validate category existence before operations.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, description FROM categories WHERE id = ?',
            (category_id,)
        )
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error in get_category_by_id: {e}")
        return None
    finally:
        if conn:
            conn.close()
            