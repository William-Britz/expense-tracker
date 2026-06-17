# Changelog

Changes are listed newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

Phase 7 in progress — integration, testing and finalisation.

---

## [0.6.0] — 2026-06-17 — Phase 6: Charts Module

### Added
- `charts/charts.py` — two chart builder functions: `build_pie_chart()` and
  `build_bar_chart()`, both returning `FigureCanvasTkAgg` for embedding in
  Tkinter. Colour palette defined locally so this module has no dependency
  on `gui/app.py`

### Fixed
- Memory leak in original guide — each chart refresh created a new Matplotlib
  figure that was never released. `plt.close(fig)` now called immediately
  after canvas creation to release the figure from Matplotlib's internal
  figure manager
- `max(totals)` called unsafely in bar label offset calculation — would raise
  `ValueError` on an empty list. Fixed with `max_val = max(totals) if totals else 0`
  and a safe fallback offset of `1` when `max_val` is zero

### Best Practices
- `matplotlib.use('TkAgg')` called before any pyplot import — required for
  Tkinter embedding. If not set first, Matplotlib picks a default backend
  with no Tkinter integration
- Y axis labels formatted as `R1,500` via `FuncFormatter` to match the
  currency format used throughout the application
- Top and right spines removed from bar chart — cleaner appearance on dark
  background, standard practice for minimal chart design
- 12 chart colours defined to cover any number of categories beyond the
  8 defaults seeded by `setup_db.py`

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
- Role enforcement checked at both GUI layer and logic layer
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
  regardless of how the request is made

### Best Practices
- All functions use `conn = None` with `finally` block — connection
  guaranteed to close on both success and failure, no leaks
- `sqlite3.IntegrityError` caught separately from `sqlite3.Error` in
  `add_category()` and `delete_category()`
- User input sanitised with `.strip()` in `add_category()` before storage
- Role enforcement at the data layer in all write operations

---

## [0.3.1] — 2026-06-17 — Hotfix: Database File and Gitignore

### Fixed
- `expensetracker.db` was committed to version control in the Phase 3
  commit due to `*.db` being missing from `.gitignore`. Removed from
  tracking with `git rm --cached` and deleted from the GitHub repository
- `.gitignore` rewritten from scratch — replaced the bloated GitHub Python
  template with a clean project-specific file

---

## [0.3.0] — 2026-06-17 — Phase 3: Authentication Layer

### Added
- `logic/auth.py` — `login()`, `logout()`, `is_admin()`, `require_login()`
  and `register_user()` with a module-level `session` dictionary
- `CHANGELOG.md` — this file

### Fixed
- Missing `import sqlite3` in `auth.py`
- `register_user()` caught bare `Exception` — now catches
  `sqlite3.IntegrityError` and `sqlite3.Error` separately
- `register_user()` and `login()` connections moved to `finally` blocks

### Security
- Passwords hashed with `bcrypt.hashpw()` and `gensalt()` on registration.
  `bcrypt.checkpw()` on login. Stored hash never decoded.

### Tested
- 5 assertions: admin login, standard user login, wrong password,
  non-existent username and empty credentials. All passed.

---

## [0.2.0] — 2026-06-16 — Phase 2: Database Layer

### Added
- `database/schema.sql` — four tables with foreign keys, CHECK constraints
  and AUTOINCREMENT PKs
- `database/db_connect.py` — single connection factory
- `setup_db.py` — creates tables and seeds default data

### Improved Over Original Guide
- `NOT NULL` on all `created_at` columns
- Three explicit indexes on `expenses` — SQLite does not auto-index FKs
- `UNIQUE(user_id, category_id, month_year)` on `budgets`
- `DEFAULT 'user'` on `role` column
- `FileNotFoundError` raised immediately if `schema.sql` is missing
- `executescript()` wrapped in `try/except` with `finally` block
- `conn.rollback()` on seed failure
- Plain-text password output removed from terminal

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
  locally