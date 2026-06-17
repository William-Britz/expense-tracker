# gui/login_screen.py
# Author  : William
# Version : 1.4
#
# Login screen. First screen the user sees on launch.
# Calls logic/auth.py login() — no database access here.
# On success, navigates to the dashboard.
# On failure, displays an inline error and clears the password field.

import tkinter as tk
from gui.app import COLORS, FONTS
from logic.auth import login


class LoginScreen(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=COLORS['bg'])
        self._build()

    def _build(self) -> None:

        outer = tk.Frame(self, bg=COLORS['bg'])
        outer.place(relx=0.5, rely=0.5, anchor='center')

        panel = tk.Frame(outer, bg=COLORS['panel'], padx=48, pady=44)
        panel.pack()

        # Spaces between letters simulate letter-spacing —
        # Tkinter has no native letter-spacing property.
        tk.Label(
            panel, text="E X P E N S E  T R A C K E R",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['panel'], fg=COLORS['accent']
        ).pack(pady=(0, 2))

        # Thin accent rule under the title
        tk.Frame(panel, bg=COLORS['accent'], height=1).pack(
            fill='x', pady=(0, 4)
        )

        tk.Label(
            panel, text="Sign in to continue",
            font=('Segoe UI', 9),
            bg=COLORS['panel'], fg=COLORS['text_dim']
        ).pack(pady=(0, 28))

        tk.Label(
            panel, text="USERNAME",
            font=('Segoe UI', 8, 'bold'),
            bg=COLORS['panel'], fg=COLORS['text_dim']
        ).pack(anchor='w')

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            panel, textvariable=self.username_var,
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=32
        )
        self.username_entry.pack(pady=(4, 16), ipady=7)

        tk.Label(
            panel, text="PASSWORD",
            font=('Segoe UI', 8, 'bold'),
            bg=COLORS['panel'], fg=COLORS['text_dim']
        ).pack(anchor='w')

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            panel, textvariable=self.password_var, show='*',
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=32
        )
        self.password_entry.pack(pady=(4, 24), ipady=7)

        self.error_var = tk.StringVar()
        tk.Label(
            panel, textvariable=self.error_var,
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['error']
        ).pack(pady=(0, 10))

        tk.Button(
            panel, text="LOGIN",
            font=('Segoe UI', 11, 'bold'),
            bg=COLORS['accent'], fg=COLORS['bg'],
            relief='flat', activebackground=COLORS['accent_dark'],
            cursor='hand2', command=self._attempt_login
        ).pack(fill='x', ipady=10)

        self.username_entry.bind(
            '<Tab>',
            lambda e: self.password_entry.focus() or 'break'
        )

        self.master.bind('<Return>', lambda e: self._attempt_login())
        self.username_entry.focus()

    def _attempt_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()

        result = login(username, password)

        if result['success']:
            self.master.unbind('<Return>')
            self.master.show_dashboard()
        else:
            self.error_var.set(result['message'])
            self.password_var.set('')
            self.password_entry.focus()