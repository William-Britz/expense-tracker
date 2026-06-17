# Changelog

Changes are listed newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

Phase 6 in progress — Matplotlib charts and reports.

---

## [0.5.0] — 2026-06-17 — Phase 5: GUI with Tkinter

### Added
- `gui/app.py` — root Tkinter window, global `COLORS` and `FONTS` constants,
  screen switcher via `show_frame()`, deferred imports per navigation method,
  `WM_DELETE_WINDOW` protocol handler for clean shutdown
- `gui/login_screen.py` — login form with masked password field, stable error
  label, Tab order with `'break'` return, Enter key binding, focus on load,
  password cleared and focus returned on failed login
- `gui/dashboard.py` — expense Treeview with scrollbar, alternating row
  colours, double-click to edit, Delete key to delete, Refresh button,
  role-gated admin panel with category add form and existing category listbox,
  `style.map` for correct selected row colour on dark theme
- `gui/expense_form.py` — shared add/edit form, validation extracted into
  `_validate()` returning `tuple[bool, str]`, Escape key to cancel, empty
  category list guard, Enter re-bound after failed validation
- `gui/reports_screen.py` — two embedded Matplotlib charts side by side,
  Refresh button rebuilds charts from fresh data, Escape to go back, try/except
  per chart so one failure does not crash the screen, summary totals bar,
  export hint label

### Fixed
- `logic/expenses.py` — added `get_expense_by_id()` function. The expense
  form previously called `get_expenses()` to find one record, fetching every
  expense for the user unnecessarily. `get_expense_by_id()` runs a single
  targeted query by ID with a JOIN on categories and users
- `gui/expense_form.py` — `_populate()` now uses `get_expense_by_id()` and
  handles a `None` return gracefully with an error message and redirect

### Best Practices
- No SQL in any GUI file — all data operations go through the logic layer
- No bare `Exception` catches in any GUI file
- All keyboard bindings unbound before navigating away to prevent
  them firing unexpectedly on the next screen
- Role enforcement checked at both GUI layer and logic layer — never
  relying on the UI alone to restrict access
- All methods have return type hints throughout all five files

---

## [0.4.0] — 2026-06-17 — Phase 4: Application Logic

### Added
- `logic/expenses.py` — six functions covering all expense data operations:
  `add_expense()`, `get_expenses()` with optional filters, `edit_expense()`,
  `delete_expense()`, `get_summary_by_category()` and `get_monthly_totals()`
- `logic/categories.py` — four functions: `get_all_categories()`,
  `add_category()`, `delete_category()` and `get_category_by_id()`

### Security
- Fixed SQL injection vulnerability in `get_monthly_totals()` — the original
  guide injected `user_id` directly into the SQL string using an f-string.
  Replaced with parameterised query using `?` placeholder and params list
- Ownership checks in `edit_expense()` and `delete_expense()` enforced at
  the database layer. A user cannot edit or delete another user's expense
  regardless of how the request is made — not relying on the GUI alone

### Best Practices
- All functions use `conn = None` with `finally` block — connection
  guaranteed to close on both success and failure, no leaks
- `sqlite3.IntegrityError` caught separately from `sqlite3.Error` in
  `add_category()` and `delete_category()` — returns a meaningful message
  for constraint violations rather than a generic error
- User input sanitised with `.strip()` in `add_category()` before storage
  to prevent whitespace variants creating duplicate category names
- Role enforcement at the data layer in all write operations — admin check
  happens before any SQL executes, not just at the GUI level

---

## [0.3.1] — 2026-06-17 — Hotfix: Database File and Gitignore

### Fixed
- `expensetracker.db` was committed to version control in the Phase 3
  commit due to `*.db` being missing from `.gitignore`. Removed from
  tracking with `git rm --cached` and deleted from the GitHub repository
- `.gitignore` rewritten from scratch — replaced the bloated GitHub Python
  template with a clean project-specific file. Added `*.db`, `*.db-journal`
  and `.vscode/settings.json` explicitly

---

## [0.3.0] — 2026-06-17 — Phase 3: Authentication Layer

### Added
- `logic/auth.py` — `login()`, `logout()`, `is_admin()`, `require_login()`
  and `register_user()` with a module-level `session` dictionary tracking
  the active user across all modules without passing state through arguments
- `CHANGELOG.md` — this file

### Fixed
- Missing `import sqlite3` in `auth.py` — `IntegrityError` was unhandled
- `register_user()` caught bare `Exception`, swallowing every failure into
  one useless generic message. Now catches `sqlite3.IntegrityError` for
  duplicate usernames and `sqlite3.Error` for all other failures separately
- `register_user()` and `login()` connections not guaranteed to close on
  failure — moved to `finally` blocks using `conn = None` pattern

### Security
- Passwords hashed with `bcrypt.hashpw()` and `gensalt()` on registration.
  `bcrypt.checkpw()` on login. Stored hash is never decoded at any point.

### Tested
- 5 assertions run against live database: admin login, standard user login,
  wrong password, non-existent username and empty credentials. All passed.

---

## [0.2.0] — 2026-06-16 — Phase 2: Database Layer

### Added
- `database/schema.sql` — four tables: `users`, `categories`, `expenses`
  and `budgets` with foreign keys, CHECK constraints and AUTOINCREMENT PKs
- `database/db_connect.py` — single connection factory exposing
  `get_connection()` and `DB_PATH` used by every module
- `setup_db.py` — reads schema, creates all tables and seeds default data

### Improved Over Original Guide
- `schema.sql` — `NOT NULL` added to all `created_at` columns. Original
  left them nullable allowing silent incomplete row inserts
- `schema.sql` — three explicit indexes on `expenses`:
  `idx_expenses_user_id`, `idx_expenses_category_id` and `idx_expenses_date`.
  SQLite does not auto-index foreign keys — without these every JOIN and
  WHERE does a full table scan
- `schema.sql` — `UNIQUE(user_id, category_id, month_year)` on `budgets`.
  Original had no uniqueness check allowing duplicate budget rows for the
  same month
- `schema.sql` — `DEFAULT 'user'` on `role` column so new accounts default
  to standard access unless explicitly set to admin
- `setup_db.py` — `FileNotFoundError` raised immediately if `schema.sql`
  is missing instead of failing deep in the stack with no context
- `setup_db.py` — `executescript()` wrapped in `try/except sqlite3.Error`
  with `finally` block — previously a failed statement left the connection
  open with no useful output
- `setup_db.py` — `conn.rollback()` on seed failure prevents partial data
  being committed
- `setup_db.py` — removed plain-text password output from terminal.
  Printing credentials to stdout is poor practice regardless of environment

---

## [0.1.0] — 2026-06-16 — Phase 1: Project Foundation

### Added
- GitHub repo: `William-Britz/expense-tracker` — public, MIT licence
- Folder structure: `database/`, `logic/`, `gui/`, `charts/`, `assets/`
- Python 3.11 virtual environment via `py -3.11 -m venv .venv`
- `matplotlib` and `bcrypt` installed and pinned in `requirements.txt`
- Custom `.gitignore` entries: `*.db` and `.vscode/settings.json`

### Notes
- Python 3.11 used explicitly — system default was 3.14 alpha with no
  stable binary wheels for `bcrypt` or `matplotlib`
- `.db` excluded from version control — each developer runs `setup_db.py`
  locally to generate their own database instance