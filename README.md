# ExpenseTracker

A desktop expense tracking application built with Python, SQLite, Tkinter and Matplotlib. Features user authentication with role-based access, full expense management and live spending charts.

---

## Features

- Secure login with bcrypt-hashed passwords
- Role-based access — admin and standard user roles
- Add, edit and delete expense entries
- Category management (admin only)
- Spending breakdown pie chart by category
- Monthly spending bar chart
- Local SQLite database with auto-increment primary keys
- Automatic first-run database setup

---

## Requirements

- Python 3.11 or higher
- Git

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/William-Britz/expense-tracker.git
cd expense-tracker
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the application**
```bash
python main.py
```

The database is created and seeded automatically on first run.

---

## Default Accounts

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |
| demo_user | user123 | User |

Change default passwords after first login.

---

## Project Structure
expense-tracker/
├── database/
│   ├── schema.sql          # SQLite schema — all tables, constraints, indexes
│   └── db_connect.py       # Connection factory used by all modules
├── logic/
│   ├── auth.py             # Login, logout, session, role checks
│   ├── expenses.py         # Expense CRUD and reporting queries
│   └── categories.py       # Category management
├── gui/
│   ├── app.py              # Root window, colour scheme, screen switcher
│   ├── login_screen.py     # Login form
│   ├── dashboard.py        # Main expense list and admin panel
│   ├── expense_form.py     # Add and edit expense form
│   └── reports_screen.py   # Charts and summary screen
├── charts/
│   └── charts.py           # Matplotlib pie and bar chart builders
├── main.py                 # Application entry point
├── setup_db.py             # Database initialisation and seed script
└── requirements.txt        # Python dependencies
---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| GUI | Tkinter |
| Database | SQLite 3 |
| Charts | Matplotlib |
| Security | bcrypt |
| Version Control | Git and GitHub |