-- =============================================================
-- ExpenseTracker Database Schema
-- Engine  : SQLite 3
-- Author  : William
-- Version : 1.0
-- =============================================================

-- SQLite does not enforce foreign keys by default.
-- This PRAGMA must be run on every connection.
-- It is also enforced in db_connect.py as a second layer.
PRAGMA foreign_keys = ON;


-- -------------------------------------------------------------
-- TABLE: users
-- Stores login credentials and role for every user.
-- role is restricted to admin or user via CHECK constraint.
-- password_hash stores the bcrypt hash, never plain text.
-- DEFAULT user means new accounts are standard unless specified.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    role            TEXT    NOT NULL DEFAULT 'user'
                            CHECK(role IN ('admin', 'user')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- -------------------------------------------------------------
-- TABLE: categories
-- Expense categories managed by admin users only.
-- name is UNIQUE, no duplicate categories permitted.
-- ON DELETE RESTRICT prevents removal of categories
-- that have expenses referencing them.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT
);


-- -------------------------------------------------------------
-- TABLE: expenses
-- Core table. Each row is one expense owned by one user
-- and assigned to one category.
-- ON DELETE CASCADE: deleting a user removes their expenses.
-- ON DELETE RESTRICT: cannot delete a category in active use.
-- amount CHECK rejects zero and negative values at DB level.
-- expense_date stored as TEXT in ISO format YYYY-MM-DD.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    category_id     INTEGER NOT NULL,
    amount          REAL    NOT NULL CHECK(amount > 0),
    description     TEXT,
    expense_date    TEXT    NOT NULL DEFAULT (date('now')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT
);

-- Explicit indexes on foreign key columns.
-- SQLite does not auto-index foreign keys.
-- Without these, every JOIN and WHERE clause does a full table scan.
CREATE INDEX IF NOT EXISTS idx_expenses_user_id
    ON expenses(user_id);

CREATE INDEX IF NOT EXISTS idx_expenses_category_id
    ON expenses(category_id);

CREATE INDEX IF NOT EXISTS idx_expenses_date
    ON expenses(expense_date);


-- -------------------------------------------------------------
-- TABLE: budgets
-- Optional monthly spend cap per user per category.
-- UNIQUE on (user_id, category_id, month_year) prevents
-- duplicate budget entries for the same month.
-- month_year stored as TEXT in format YYYY-MM.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS budgets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    category_id     INTEGER NOT NULL,
    month_year      TEXT    NOT NULL,
    amount          REAL    NOT NULL CHECK(amount > 0),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, category_id, month_year),
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT
);