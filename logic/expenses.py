# logic/expenses.py
# Author  : William
# Version : 1.1
#
# All expense data operations for ExpenseTracker.
# The GUI never touches the database directly — it calls these
# functions only. All SQL lives here and nowhere else.

import sqlite3
from database.db_connect import get_connection
from logic.auth import session, is_admin


def add_expense(
    category_id: int,
    amount: float,
    description: str,
    expense_date: str
) -> dict:
    """
    Add a new expense for the currently logged-in user.
    expense_date must be a string in ISO format: YYYY-MM-DD.
    Returns a success/failure dict.
    """
    user_id = session['user_id']
    if not user_id:
        return {'success': False, 'message': 'Not logged in.'}

    conn = None
    try:
        conn = get_connection()
        conn.execute(
            'INSERT INTO expenses '
            '(user_id, category_id, amount, description, expense_date) '
            'VALUES (?, ?, ?, ?, ?)',
            (user_id, category_id, amount, description, expense_date)
        )
        conn.commit()
        return {'success': True, 'message': 'Expense added.'}
    except sqlite3.Error as e:
        return {'success': False, 'message': f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()


def get_expenses(filters: dict = None) -> list:
    """
    Fetch expenses for the current user (or all users if admin).
    Optional filters dict keys: category_id, start_date, end_date.
    Returns a list of sqlite3.Row objects — access columns by name.
    """
    user_id = session['user_id']
    params = []
    conditions = []

    # Admins see all expenses. Standard users only see their own.
    # This is role-based data scoping — enforced in the query itself,
    # not just in the GUI. Never rely on the UI alone to restrict data.
    if not is_admin():
        conditions.append('e.user_id = ?')
        params.append(user_id)

    if filters:
        if filters.get('category_id'):
            conditions.append('e.category_id = ?')
            params.append(filters['category_id'])
        if filters.get('start_date'):
            conditions.append('e.expense_date >= ?')
            params.append(filters['start_date'])
        if filters.get('end_date'):
            conditions.append('e.expense_date <= ?')
            params.append(filters['end_date'])

    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''

    sql = f'''
        SELECT
            e.id,
            e.amount,
            e.description,
            e.expense_date,
            c.name  AS category_name,
            u.username
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        JOIN users      u ON e.user_id     = u.id
        {where_clause}
        ORDER BY e.expense_date DESC, e.created_at DESC
    '''

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error in get_expenses: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_expense_by_id(expense_id: int):
    """
    Fetch a single expense row by ID.
    Returns a sqlite3.Row or None if not found.
    Used by the expense form to pre-populate fields in edit mode.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT
                e.id,
                e.amount,
                e.description,
                e.expense_date,
                c.name AS category_name,
                u.username
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            JOIN users      u ON e.user_id     = u.id
            WHERE e.id = ?
            ''',
            (expense_id,)
        )
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error in get_expense_by_id: {e}")
        return None
    finally:
        if conn:
            conn.close()


def edit_expense(
    expense_id: int,
    category_id: int,
    amount: float,
    description: str,
    expense_date: str
) -> dict:
    """
    Update an existing expense.
    Standard users can only edit their own expenses.
    Admins can edit any expense.
    Returns a success/failure dict.
    """
    user_id = session['user_id']

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verify ownership before allowing the edit.
        # This check happens at the database layer, not just the GUI.
        # A user who bypasses the GUI would still be blocked here.
        cursor.execute(
            'SELECT user_id FROM expenses WHERE id = ?',
            (expense_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return {'success': False, 'message': 'Expense not found.'}

        if not is_admin() and row['user_id'] != user_id:
            return {'success': False, 'message': 'Permission denied.'}

        cursor.execute(
            'UPDATE expenses '
            'SET category_id = ?, amount = ?, description = ?, expense_date = ? '
            'WHERE id = ?',
            (category_id, amount, description, expense_date, expense_id)
        )
        conn.commit()
        return {'success': True, 'message': 'Expense updated.'}

    except sqlite3.Error as e:
        return {'success': False, 'message': f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()


def delete_expense(expense_id: int) -> dict:
    """
    Delete an expense by ID.
    Standard users can only delete their own expenses.
    Admins can delete any expense.
    Returns a success/failure dict.
    """
    user_id = session['user_id']

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT user_id FROM expenses WHERE id = ?',
            (expense_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return {'success': False, 'message': 'Expense not found.'}

        if not is_admin() and row['user_id'] != user_id:
            return {'success': False, 'message': 'Permission denied.'}

        cursor.execute(
            'DELETE FROM expenses WHERE id = ?',
            (expense_id,)
        )
        conn.commit()
        return {'success': True, 'message': 'Expense deleted.'}

    except sqlite3.Error as e:
        return {'success': False, 'message': f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()


def get_summary_by_category(
    start_date: str = None,
    end_date: str = None
) -> list:
    """
    Returns total spending per category for the current user
    (or all users if admin). Used by the pie chart.
    Returns a list of dicts: [{'category': str, 'total': float}, ...]
    """
    user_id = session['user_id']
    params = []
    conditions = []

    if not is_admin():
        conditions.append('e.user_id = ?')
        params.append(user_id)
    if start_date:
        conditions.append('e.expense_date >= ?')
        params.append(start_date)
    if end_date:
        conditions.append('e.expense_date <= ?')
        params.append(end_date)

    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''

    sql = f'''
        SELECT c.name AS category, SUM(e.amount) AS total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        {where_clause}
        GROUP BY c.name
        ORDER BY total DESC
    '''

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return [
            {'category': r['category'], 'total': r['total']}
            for r in cursor.fetchall()
        ]
    except sqlite3.Error as e:
        print(f"Database error in get_summary_by_category: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_monthly_totals() -> list:
    """
    Returns total spending per month for the current user
    (or all users if admin). Used by the bar chart.
    Returns a list of dicts: [{'month': 'YYYY-MM', 'total': float}, ...]
    """
    user_id = session['user_id']

    # Parameterised query used here — this was a SQL injection
    # vulnerability in the original guide which used an f-string
    # to inject user_id directly into the SQL string.
    # The correct approach is always ? placeholders with a params list.
    params = []
    where_clause = ''

    if not is_admin():
        where_clause = 'WHERE e.user_id = ?'
        params.append(user_id)

    sql = f'''
        SELECT
            strftime('%Y-%m', e.expense_date) AS month,
            SUM(e.amount) AS total
        FROM expenses e
        {where_clause}
        GROUP BY month
        ORDER BY month ASC
    '''

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return [
            {'month': r['month'], 'total': r['total']}
            for r in cursor.fetchall()
        ]
    except sqlite3.Error as e:
        print(f"Database error in get_monthly_totals: {e}")
        return []
    finally:
        if conn:
            conn.close()