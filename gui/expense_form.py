# gui/expense_form.py
# Author  : William
# Version : 1.1
#
# Add and edit expense form. Handles both modes with one screen.
# If expense_id is None the form is in add mode.
# If expense_id is an int the form pre-populates for editing.
# Calls logic/expenses.py and logic/categories.py — no SQL here.

import tkinter as tk
from tkinter import messagebox
from datetime import date
from gui.app import COLORS, FONTS
from logic.expenses import add_expense, edit_expense, get_expense_by_id
from logic.categories import get_all_categories


class ExpenseForm(tk.Frame):
    """
    Shared add/edit expense form. Inherits from tk.Frame so it can be
    managed by App.show_frame() like any other screen.
    """

    def __init__(self, master, expense_id=None):
        super().__init__(master, bg=COLORS['bg'])
        self.expense_id = expense_id
        self.categories = get_all_categories()
        self._build()
        if self.expense_id is not None:
            self._populate()

    def _build(self) -> None:
        """Build and place all widgets for the expense form."""

        outer = tk.Frame(self, bg=COLORS['bg'])
        outer.place(relx=0.5, rely=0.5, anchor='center')

        panel = tk.Frame(outer, bg=COLORS['panel'], padx=40, pady=36)
        panel.pack()

        title = "Edit Expense" if self.expense_id is not None else "Add Expense"
        tk.Label(
            panel, text=title,
            font=FONTS['title'], bg=COLORS['panel'], fg=COLORS['accent']
        ).pack(pady=(0, 24))

        # ── Category dropdown ─────────────────────────────────────────────────
        tk.Label(
            panel, text="Category",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(anchor='w')

        self.cat_names = [c['name'] for c in self.categories]
        self.cat_ids   = [c['id']   for c in self.categories]

        default_cat = self.cat_names[0] if self.cat_names else ''
        self.cat_var = tk.StringVar(value=default_cat)

        cat_menu = tk.OptionMenu(panel, self.cat_var, *self.cat_names)
        cat_menu.config(
            bg=COLORS['entry_bg'], fg=COLORS['text'],
            font=FONTS['body'], relief='flat',
            highlightthickness=0,
            activebackground=COLORS['accent_dark'],
            activeforeground=COLORS['text']
        )
        cat_menu['menu'].config(
            bg=COLORS['entry_bg'], fg=COLORS['text'],
            activebackground=COLORS['accent_dark'],
            activeforeground=COLORS['text']
        )
        cat_menu.pack(fill='x', pady=(2, 12))

        # ── Amount field ──────────────────────────────────────────────────────
        tk.Label(
            panel, text="Amount (R)",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(anchor='w')

        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(
            panel, textvariable=self.amount_var,
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=30
        )
        self.amount_entry.pack(pady=(2, 12), ipady=6)

        # ── Description field ─────────────────────────────────────────────────
        tk.Label(
            panel, text="Description",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(anchor='w')

        self.desc_var = tk.StringVar()
        tk.Entry(
            panel, textvariable=self.desc_var,
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=30
        ).pack(pady=(2, 12), ipady=6)

        # ── Date field ────────────────────────────────────────────────────────
        tk.Label(
            panel, text="Date (YYYY-MM-DD)",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(anchor='w')

        self.date_var = tk.StringVar(value=str(date.today()))
        tk.Entry(
            panel, textvariable=self.date_var,
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=30
        ).pack(pady=(2, 20), ipady=6)

        # ── Error label ───────────────────────────────────────────────────────
        self.error_var = tk.StringVar()
        tk.Label(
            panel, textvariable=self.error_var,
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['error']
        ).pack(pady=(0, 8))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = tk.Frame(panel, bg=COLORS['panel'])
        btn_row.pack(fill='x')

        tk.Button(
            btn_row, text="Cancel",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text_dim'],
            relief='flat', cursor='hand2',
            command=self._cancel
        ).pack(side='left', padx=(0, 12))

        tk.Button(
            btn_row, text="Save",
            font=FONTS['heading'], bg=COLORS['accent'], fg=COLORS['bg'],
            relief='flat', cursor='hand2', command=self._save
        ).pack(side='left', fill='x', expand=True, ipady=6)

        self.amount_entry.focus()
        self.master.bind('<Return>', lambda e: self._save())
        self.master.bind('<Escape>', lambda e: self._cancel())

    def _cancel(self) -> None:
        """Clean up bindings and return to the dashboard."""
        self.master.unbind('<Return>')
        self.master.unbind('<Escape>')
        self.master.show_dashboard()

    def _populate(self) -> None:
        """
        Pre-fill the form fields when in edit mode.
        Uses get_expense_by_id() to fetch only the required row —
        not get_expenses() which fetches every expense unnecessarily.
        """
        exp = get_expense_by_id(self.expense_id)
        if exp is None:
            messagebox.showerror(
                "Error", "Expense not found. It may have been deleted."
            )
            self._cancel()
            return

        self.amount_var.set(str(exp['amount']))
        self.desc_var.set(exp['description'] or '')
        self.date_var.set(exp['expense_date'])
        if exp['category_name'] in self.cat_names:
            self.cat_var.set(exp['category_name'])

    def _validate(self) -> tuple[bool, str]:
        """
        Validate all form fields before saving.
        Returns (is_valid, error_message).
        Validation lives here to keep _save() clean and readable.
        """
        # Guard against empty category list
        if not self.cat_names:
            return False, "No categories available. Ask an admin to add one."

        if not self.cat_var.get() or self.cat_var.get() not in self.cat_names:
            return False, "Select a valid category."

        # Amount must be a positive number
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            return False, "Amount must be a positive number."

        # Date format check — YYYY-MM-DD
        expense_date = self.date_var.get().strip()
        if len(expense_date) != 10 or expense_date[4] != '-' or expense_date[7] != '-':
            return False, "Date must be in format YYYY-MM-DD."

        try:
            year, month, day = expense_date.split('-')
            if not (1900 <= int(year) <= 2100):
                raise ValueError
            if not (1 <= int(month) <= 12):
                raise ValueError
            if not (1 <= int(day) <= 31):
                raise ValueError
        except ValueError:
            return False, "Enter a valid date in format YYYY-MM-DD."

        return True, ''

    def _save(self) -> None:
        """Validate the form and call the correct logic function."""
        self.master.unbind('<Return>')

        is_valid, error_message = self._validate()
        if not is_valid:
            self.error_var.set(error_message)
            self.master.bind('<Return>', lambda e: self._save())
            return

        cat_id       = self.cat_ids[self.cat_names.index(self.cat_var.get())]
        amount       = float(self.amount_var.get())
        description  = self.desc_var.get().strip()
        expense_date = self.date_var.get().strip()

        if self.expense_id is not None:
            result = edit_expense(
                self.expense_id, cat_id, amount, description, expense_date
            )
        else:
            result = add_expense(cat_id, amount, description, expense_date)

        if result['success']:
            self.master.unbind('<Escape>')
            self.master.show_dashboard()
        else:
            self.error_var.set(result['message'])
            self.master.bind('<Return>', lambda e: self._save())