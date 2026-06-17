# logic/auth.py
# Author  : William
# Version : 1.1
#
# Authentication module. Handles login, logout, session state
# and role-based access control for the entire application.
# Every other module imports from here to check who is logged in
# and what they are permitted to do.

import sqlite3
import bcrypt
from database.db_connect import get_connection


# Session dictionary — holds the currently logged-in user's data.
# All values reset to None on logout or before any login occurs.
session = {
    'user_id':   None,
    'username':  None,
    'role':      None,
    'logged_in': False
}


def login(username: str, password: str) -> dict:
    """
    Attempt to authenticate a user against the database.
    Returns a dict with keys: success (bool), message (str), role (str or None).
    Populates the session dictionary on success.
    """
    if not username or not password:
        return {
            'success': False,
            'message': 'Username and password are required.',
            'role':    None
        }

    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, password_hash, role '
            'FROM users WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}",
            'role':    None
        }
    finally:
        if conn:
            conn.close()

    if user is None:
        return {
            'success': False,
            'message': 'Username not found.',
            'role':    None
        }

    # bcrypt.checkpw hashes the plain-text input and compares it
    # to the stored hash. The stored hash is never decoded.
    password_matches = bcrypt.checkpw(
        password.encode(),
        user['password_hash'].encode()
    )

    if not password_matches:
        return {
            'success': False,
            'message': 'Incorrect password.',
            'role':    None
        }

    # Populate session on successful login
    session['user_id']   = user['id']
    session['username']  = user['username']
    session['role']      = user['role']
    session['logged_in'] = True

    return {
        'success': True,
        'message': f"Welcome, {user['username']}.",
        'role':    user['role']
    }


def logout() -> None:
    """Clear the session. Called when the user clicks Logout."""
    session['user_id']   = None
    session['username']  = None
    session['role']      = None
    session['logged_in'] = False


def is_admin() -> bool:
    """Returns True if the current session user has the admin role."""
    return session.get('role') == 'admin'


def require_login() -> bool:
    """Returns True if a user is currently logged in."""
    return session.get('logged_in', False)


def register_user(username: str, password: str, role: str = 'user') -> dict:
    """
    Create a new user account. Intended for admin use only.
    Passwords are bcrypt-hashed before storage.
    Returns a success/failure dict with a descriptive message.
    """
    if not username or not password:
        return {
            'success': False,
            'message': 'Username and password are required.'
        }

    if role not in ('admin', 'user'):
        return {
            'success': False,
            'message': 'Role must be admin or user.'
        }

    password_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()

    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) '
            'VALUES (?, ?, ?)',
            (username, password_hash, role)
        )
        conn.commit()
        return {
            'success': True,
            'message': f"User '{username}' created successfully."
        }
    except sqlite3.IntegrityError:
        # Triggered when username already exists due to UNIQUE constraint
        return {
            'success': False,
            'message': f"Username '{username}' is already taken."
        }
    except sqlite3.Error as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }
    finally:
        if conn:
            conn.close()