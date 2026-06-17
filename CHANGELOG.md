# Changelog

Changes are listed newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

Nothing in progress.

---

## [0.3.1] — 2026-06-17 — Hotfix: database file and gitignore

### Fixed
- `expensetracker.db` was committed to version control in the Phase 3
  commit due to `*.db` being missing from `.gitignore`. Removed from
  tracking with `git rm --cached` and deleted from GitHub history
- `.gitignore` rewritten from scratch — replaced the bloated GitHub
  Python template with a clean, project-specific file. Added `*.db`,
  `*.db-journal` and `.vscode/settings.json` explicitly. Removed
  hundreds of lines of irrelevant framework entries

---

## [0.3.0] — 2026-06-17 — Phase 3: Authentication Layer

### Added
- `logic/auth.py` — `login()`, `logout()`, `is_admin()`, `require_login()`
  and `register_user()` with a module-level `session` dictionary tracking
  the active user across all modules without passing state through arguments
- `CHANGELOG.md` — this file, tracking all changes from project start

### Fixed
- Missing `import sqlite3` in `auth.py` — `IntegrityError` was unhandled
- `register_user()` caught bare `Exception`, swallowing every failure into
  one useless message. Now catches `sqlite3.IntegrityError` for duplicate
  usernames and `sqlite3.Error` for everything else separately
- `register_user()` connection not guaranteed to close on failure — moved
  to `finally` block using `conn = None` pattern to prevent leaks
- `login()` database connection now also uses `conn = None` pattern with
  `finally` block for consistent connection handling across all functions

### Security
- Passwords hashed with `bcrypt.hashpw()` and `gensalt()` on registration.
  `bcrypt.checkpw()` on login. Stored hash is never decoded at any point.

### Tested
- 5 test cases run against live database: admin login, standard user login,
  wrong password, non-existent username and empty credentials. All passed.

---

## [0.2.0] — 2026-06-16 — Phase 2: Database Layer

### Added
- `database/schema.sql` — four tables: `users`, `categories`, `expenses`
  and `budgets` with foreign keys, CHECK constraints and AUTOINCREMENT PKs
- `database/db_connect.py` — single connection factory, `get_connection()`
  and `DB_PATH` used by every module that touches the database
- `setup_db.py` — reads schema, creates tables and seeds default data

### Improved over original guide
- `schema.sql` — `NOT NULL` added to all `created_at` columns. Original
  left them nullable allowing silent incomplete row inserts
- `schema.sql` — three explicit indexes added on `expenses`:
  `idx_expenses_user_id`, `idx_expenses_category_id` and `idx_expenses_date`.
  SQLite does not auto-index foreign keys. Without these every JOIN and
  WHERE does a full table scan
- `schema.sql` — `UNIQUE(user_id, category_id, month_year)` added to
  `budgets`. Original had no uniqueness check allowing duplicate budget
  rows for the same month to be inserted silently
- `schema.sql` — `DEFAULT 'user'` on `role` column so new accounts
  default to standard access unless explicitly set to admin
- `setup_db.py` — `FileNotFoundError` raised immediately if `schema.sql`
  is missing instead of failing deep in the call stack with no context
- `setup_db.py` — `executescript()` wrapped in `try/except sqlite3.Error`
  with `finally` block. Previously a failed statement left the connection
  open with no useful output
- `setup_db.py` — `conn.rollback()` added on seed failure to prevent
  partial data being committed
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
- Python 3.11 used explicitly — system default was 3.14 alpha which has
  no stable binary wheels for `bcrypt` or `matplotlib`
- `.db` excluded from version control — each developer runs `setup_db.py`
  locally to generate their own database instance