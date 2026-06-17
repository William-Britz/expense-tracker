# Changelog

Changes are listed newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [1.0.0] — 2026-06-17 — Phase 7: Integration and Release

### Added
- `main.py` — application entry point with first-run database auto-setup,
  deferred Tkinter import, `sys.path` guarantee, error handling around both
  setup and launch with `sys.exit(1)` on failure
- `README.md` — full setup instructions, default accounts table, project
  structure tree and tech stack table

### Fixed
- `main.py` — `DB_PATH` import moved inside `main()` to ensure `sys.path`
  is set before any internal module is imported
- `main.py` — partial database cleanup on failed setup: if `create_tables()`
  succeeds but `seed_data()` fails, the incomplete `.db` file is removed so
  the next run triggers a clean setup rather than launching with missing data
- `main.py` — `os.makedirs(db_dir, exist_ok=True)` ensures the database
  directory exists before SQLite attempts to create the file
- `gui/login_screen.py` — switched from Arial to Segoe UI throughout.
  Field labels changed to small-caps uppercase style. Title uses spaced
  characters to simulate letter-spacing (Tkinter has no native property).
  Thin accent rule added under the title.
- `gui/app.py` — FONTS dict updated to Segoe UI across all variants.
  Consolas retained for monospace/code elements only.

### Removed
- `letterSpacing` option from `tk.Label` — not a valid Tkinter property,
  caused `unknown option` crash on launch

---

## [0.6.0] — 2026-06-17 — Phase 6: Charts Module

### Added
- `charts/charts.py` — `build_pie_chart()` and `build_bar_chart()` returning
  `FigureCanvasTkAgg` for embedding in Tkinter. Colour palette defined locally
  so this module has no dependency on `gui/app.py`

### Fixed
- Memory leak — each chart refresh created a new Matplotlib figure never
  released. `plt.close(fig)` now called after canvas creation
- `max(totals)` called unsafely — would raise `ValueError` on an empty list.
  Fixed with `max_val = max(totals) if totals else 0` and safe fallback offset

### Best Practices
- `matplotlib.use('TkAgg')` called before any pyplot import
- Y axis labels formatted as `R1,500` via `FuncFormatter`
- Top and right spines removed from bar chart
- 12 chart colours defined to cover any number of categories

---

## [0.5.0] — 2026-06-17 — Phase 5: GUI with Tkinter

### Added
- `gui/app.py` — root window, `COLORS` and `FONTS`, screen switcher,
  deferred imports, `WM_DELETE_WINDOW` handler
- `gui/login_screen.py` — masked password, stable error label, Tab order,
  Enter binding, focus on load, password cleared on failed login
- `gui/dashboard.py` — Treeview with scrollbar, double-click to edit,
  Delete key binding, Refresh button, role-gated admin panel,
  `style.map` for correct selected row colour
- `gui/expense_form.py` — shared add/edit form, `_validate()` returning
  `tuple[bool, str]`, Escape to cancel, empty category guard
- `gui/reports_screen.py` — embedded charts, Refresh button, Escape to
  go back, try/except per chart, summary totals bar

### Fixed
- Added `get_expense_by_id()` to `logic/expenses.py` — form previously
  fetched every expense to find one record
- `_populate()` handles `None` return from `get_expense_by_id()` gracefully

### Best Practices
- No SQL in any GUI file
- All keyboard bindings unbound before navigating away
- Role enforcement at both GUI and logic layer
- All methods have return type hints

---

## [0.4.0] — 2026-06-17 — Phase 4: Application Logic

### Added
- `logic/expenses.py` — `add_expense()`, `get_expenses()`, `edit_expense()`,
  `delete_expense()`, `get_summary_by_category()` and `get_monthly_totals()`
- `logic/categories.py` — `get_all_categories()`, `add_category()`,
  `delete_category()` and `get_category_by_id()`

### Security
- Fixed SQL injection in `get_monthly_totals()` — f-string replaced with
  parameterised query
- Ownership checks enforced at the database layer in edit and delete

### Best Practices
- `conn = None` with `finally` block on all functions
- `sqlite3.IntegrityError` caught separately from `sqlite3.Error`
- Input sanitised with `.strip()` before storage
- Role enforcement before any SQL executes

---

## [0.3.1] — 2026-06-17 — Hotfix: Database File and Gitignore

### Fixed
- `expensetracker.db` committed to version control — removed with
  `git rm --cached` and deleted from GitHub
- `.gitignore` rewritten — clean project-specific file replacing the
  bloated GitHub Python template

---

## [0.3.0] — 2026-06-17 — Phase 3: Authentication Layer

### Added
- `logic/auth.py` — `login()`, `logout()`, `is_admin()`, `require_login()`,
  `register_user()` and module-level `session` dictionary
- `CHANGELOG.md`

### Fixed
- Missing `import sqlite3`
- `register_user()` bare `Exception` catch replaced with specific handlers
- Connections moved to `finally` blocks

### Security
- bcrypt hashing on registration, `checkpw` on login, hash never decoded

### Tested
- 5 assertions all passed: admin login, standard user, wrong password,
  non-existent username and empty credentials

---

## [0.2.0] — 2026-06-16 — Phase 2: Database Layer

### Added
- `database/schema.sql` — four tables with FK constraints and AUTOINCREMENT
- `database/db_connect.py` — single connection factory
- `setup_db.py` — schema creation and seed data

### Improved Over Original Guide
- `NOT NULL` on all `created_at` columns
- Three explicit indexes on `expenses` — SQLite does not auto-index FKs
- `UNIQUE(user_id, category_id, month_year)` on `budgets`
- `DEFAULT 'user'` on `role` column
- `FileNotFoundError` on missing schema file
- `executescript()` in `try/except` with `finally`
- `conn.rollback()` on seed failure
- Plain-text password output removed from terminal

---

## [0.1.0] — 2026-06-16 — Phase 1: Project Foundation

### Added
- GitHub repo: `William-Britz/expense-tracker` — public, MIT licence
- Folder structure: `database/`, `logic/`, `gui/`, `charts/`, `assets/`
- Python 3.11 virtual environment via `py -3.11 -m venv .venv`
- `matplotlib` and `bcrypt` pinned in `requirements.txt`
- `.gitignore` with `*.db` and `.vscode/settings.json`

### Notes
- Python 3.11 used explicitly — system default 3.14 alpha has no stable
  wheels for `bcrypt` or `matplotlib`
- `.db` excluded from version control — each developer runs `setup_db.py`
  locally