# gui/dashboard.py
# Author  : William
# Version : 1.1
#
# Main screen after login. Shows the full expense list with
# add, edit and delete controls. Admin users see an additional
# panel on the right for category management.
# Calls logic/expenses.py and logic/categories.py — no SQL here.

import tkinter as tk
from tkinter import ttk, messagebox
from gui.app import COLORS, FONTS
from logic.auth import session, logout, is_admin
from logic.expenses import get_expenses, delete_expense
from logic.categories import get_all_categories, add_category


class Dashboard(tk.Frame):
    """
    Main dashboard screen. Inherits from tk.Frame so it can be
    managed by App.show_frame() like any other screen.
    """

    def __init__(self, master):
        super().__init__(master, bg=COLORS['bg'])
        self._build()
        self._load_expenses()

    def _build(self) -> None:
        """Build and place all widgets for the dashboard."""

        # ── Top bar ───────────────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=COLORS['panel'], height=50)
        topbar.pack(fill='x')
        topbar.pack_propagate(False)

        tk.Label(
            topbar, text="  EXPENSETRACKER",
            font=FONTS['heading'], bg=COLORS['panel'], fg=COLORS['accent']
        ).pack(side='left', padx=10)

        user_text = f"  {session['username']}  ({session['role']})  "
        tk.Label(
            topbar, text=user_text,
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim']
        ).pack(side='right', padx=4)

        tk.Button(
            topbar, text="Logout",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text'],
            relief='flat', cursor='hand2', command=self._logout
        ).pack(side='right', padx=8)

        tk.Button(
            topbar, text="Reports & Charts",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['accent'],
            relief='flat', cursor='hand2',
            command=self.master.show_reports
        ).pack(side='right', padx=8)

        # ── Main area ─────────────────────────────────────────────────────────
        main = tk.Frame(self, bg=COLORS['bg'])
        main.pack(fill='both', expand=True, padx=20, pady=16)

        # ── Left: expense list ────────────────────────────────────────────────
        left = tk.Frame(main, bg=COLORS['bg'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 16))

        hdr = tk.Frame(left, bg=COLORS['bg'])
        hdr.pack(fill='x', pady=(0, 8))

        tk.Label(
            hdr, text="Expenses",
            font=FONTS['heading'], bg=COLORS['bg'], fg=COLORS['text']
        ).pack(side='left')

        tk.Button(
            hdr, text="+ Add Expense",
            font=FONTS['small'], bg=COLORS['accent'], fg=COLORS['bg'],
            relief='flat', cursor='hand2',
            command=lambda: self.master.show_add_expense()
        ).pack(side='right')

        # ── Treeview with scrollbar ───────────────────────────────────────────
        # The Treeview and scrollbar are placed in a separate container frame
        # so they sit side by side correctly using pack.
        # Without a scrollbar, long expense lists have no way to scroll.
        tree_frame = tk.Frame(left, bg=COLORS['bg'])
        tree_frame.pack(fill='both', expand=True)

        cols = ('ID', 'Date', 'Category', 'Description', 'Amount', 'User')
        self.tree = ttk.Treeview(
            tree_frame, columns=cols, show='headings', height=22
        )

        col_widths = [40, 90, 130, 260, 90, 100]
        for col, width in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='w')

        # Scrollbar linked to the Treeview's yview method
        scrollbar = ttk.Scrollbar(
            tree_frame, orient='vertical', command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # ttk widgets use a Style object for theming rather than direct
        # colour arguments. style.map overrides colours for specific
        # widget states — here we fix the selected row highlight colour
        # to match the dark theme instead of the default system blue.
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Treeview',
            background=COLORS['panel'],
            foreground=COLORS['text'],
            fieldbackground=COLORS['panel'],
            rowheight=26,
            font=FONTS['body']
        )
        style.configure(
            'Treeview.Heading',
            background=COLORS['accent'],
            foreground=COLORS['bg'],
            font=FONTS['heading']
        )
        style.map(
            'Treeview',
            background=[('selected', COLORS['accent_dark'])]
        )
        self.tree.tag_configure('odd', background=COLORS['row_alt'])

        # Double-click a row to edit — standard desktop application behaviour.
        # <Double-1> is the Tkinter event for a left mouse double-click.
        self.tree.bind('<Double-1>', lambda e: self._edit_selected())

        # Delete key on a selected row triggers deletion.
        # Users expect this — only having a button is not enough.
        self.tree.bind('<Delete>', lambda e: self._delete_selected())

        # ── Action buttons below the table ────────────────────────────────────
        btn_frame = tk.Frame(left, bg=COLORS['bg'])
        btn_frame.pack(fill='x', pady=(8, 0))

        tk.Button(
            btn_frame, text="Edit Selected",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['accent'],
            relief='flat', cursor='hand2', command=self._edit_selected
        ).pack(side='left', padx=(0, 8))

        tk.Button(
            btn_frame, text="Delete Selected",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['error'],
            relief='flat', cursor='hand2', command=self._delete_selected
        ).pack(side='left')

        tk.Button(
            btn_frame, text="Refresh",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim'],
            relief='flat', cursor='hand2', command=self._load_expenses
        ).pack(side='right')

        # ── Right: admin panel (role-gated) ───────────────────────────────────
        # Rendered only for admin users. is_admin() checks the session.
        # The same check also exists at the logic layer in categories.py —
        # never rely on UI-only access control.
        if is_admin():
            right = tk.Frame(
                main, bg=COLORS['panel'], width=220, padx=12, pady=12
            )
            right.pack(side='right', fill='y')
            right.pack_propagate(False)

            tk.Label(
                right, text="Admin Panel",
                font=FONTS['heading'], bg=COLORS['panel'], fg=COLORS['accent']
            ).pack(anchor='w', pady=(0, 12))

            tk.Label(
                right, text="Add Category",
                font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim']
            ).pack(anchor='w')

            self.cat_name_var = tk.StringVar()
            self.cat_entry = tk.Entry(
                right, textvariable=self.cat_name_var,
                font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
                insertbackground=COLORS['text'], relief='flat'
            )
            self.cat_entry.pack(fill='x', pady=(2, 6), ipady=4)

            tk.Button(
                right, text="Add Category",
                font=FONTS['small'], bg=COLORS['accent'], fg=COLORS['bg'],
                relief='flat', cursor='hand2', command=self._add_category
            ).pack(fill='x', ipady=4)

            tk.Label(
                right, text="Existing Categories",
                font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim']
            ).pack(anchor='w', pady=(16, 4))

            self.cat_listbox = tk.Listbox(
                right,
                font=FONTS['small'], bg=COLORS['entry_bg'], fg=COLORS['text'],
                selectbackground=COLORS['accent_dark'],
                relief='flat', height=12, activestyle='none'
            )
            self.cat_listbox.pack(fill='x')
            self._load_categories()

    def _load_expenses(self) -> None:
        """Fetch all expenses and populate the Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        expenses = get_expenses()
        for i, exp in enumerate(expenses):
            tag = 'odd' if i % 2 else ''
            self.tree.insert(
                '', 'end',
                iid=str(exp['id']),
                values=(
                    exp['id'],
                    exp['expense_date'],
                    exp['category_name'],
                    exp['description'] or '',
                    f"R {exp['amount']:.2f}",
                    exp['username']
                ),
                tags=(tag,)
            )

    def _load_categories(self) -> None:
        """Populate the category listbox in the admin panel."""
        if not hasattr(self, 'cat_listbox'):
            return
        self.cat_listbox.delete(0, tk.END)
        for cat in get_all_categories():
            self.cat_listbox.insert(tk.END, cat['name'])

    def _edit_selected(self) -> None:
        """Navigate to the expense form in edit mode for the selected row."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No selection", "Select an expense to edit."
            )
            return
        expense_id = int(selected[0])
        self.master.show_add_expense(expense_id=expense_id)

    def _delete_selected(self) -> None:
        """Delete the selected expense after confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No selection", "Select an expense to delete."
            )
            return
        if not messagebox.askyesno(
            "Confirm", "Delete this expense? This cannot be undone."
        ):
            return
        expense_id = int(selected[0])
        result = delete_expense(expense_id)
        if result['success']:
            self._load_expenses()
        else:
            messagebox.showerror("Error", result['message'])

    def _add_category(self) -> None:
        """Add a new category using the admin panel input field."""
        name = self.cat_name_var.get().strip()
        if not name:
            messagebox.showwarning(
                "Input required", "Enter a category name."
            )
            return
        result = add_category(name)
        if result['success']:
            self.cat_name_var.set('')
            self.cat_entry.focus()
            self._load_categories()
            messagebox.showinfo("Done", result['message'])
        else:
            messagebox.showerror("Error", result['message'])

    def _logout(self) -> None:
        """Log out the current user and return to the login screen."""
        logout()
        self.master.show_login()