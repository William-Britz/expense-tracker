# gui/login_screen.py
# Author  : William
# Version : 1.2
#
# Login screen. First screen the user sees on launch.
# Calls logic/auth.py login() — no database access here.
# On success, navigates to the dashboard.
# On failure, displays an inline error and clears the password field.

import tkinter as tk
from gui.app import COLORS, FONTS
from logic.auth import login


class LoginScreen(tk.Frame):
    """
    Login form screen. Inherits from tk.Frame so it can be
    managed by App.show_frame() like any other screen.
    """

    def __init__(self, master):
        super().__init__(master, bg=COLORS['bg'])
        self._build()

    def _build(self) -> None:
        """Build and place all widgets for the login screen."""

        # place() positions the outer frame at the exact centre
        # of the window regardless of window size.
        # relx=0.5, rely=0.5 means 50% across and 50% down.
        # anchor='center' means the centre of the frame sits at that point.
        outer = tk.Frame(self, bg=COLORS['bg'])
        outer.place(relx=0.5, rely=0.5, anchor='center')

        panel = tk.Frame(outer, bg=COLORS['panel'], padx=40, pady=40)
        panel.pack()

        # App title
        tk.Label(
            panel, text="EXPENSETRACKER",
            font=FONTS['title'], bg=COLORS['panel'], fg=COLORS['accent']
        ).pack(pady=(0, 4))

        tk.Label(
            panel, text="Sign in to continue",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim']
        ).pack(pady=(0, 24))

        # Username field
        tk.Label(
            panel, text="Username",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(anchor='w')

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            panel, textvariable=self.username_var,
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=30
        )
        self.username_entry.pack(pady=(2, 12), ipady=6)

        # Password field — show='*' masks input as the user types.
        # Never render a password field without this.
        tk.Label(
            panel, text="Password",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(anchor='w')

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            panel, textvariable=self.password_var, show='*',
            font=FONTS['body'], bg=COLORS['entry_bg'], fg=COLORS['text'],
            insertbackground=COLORS['text'], relief='flat', width=30
        )
        self.password_entry.pack(pady=(2, 20), ipady=6)

        # Error label — always present in the layout but empty until
        # a failed login attempt. Keeps the layout stable — no jumping
        # or shifting when an error appears or disappears.
        self.error_var = tk.StringVar()
        tk.Label(
            panel, textvariable=self.error_var,
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['error']
        ).pack(pady=(0, 8))

        # Login button
        tk.Button(
            panel, text="Login",
            font=FONTS['heading'], bg=COLORS['accent'], fg=COLORS['bg'],
            relief='flat', activebackground=COLORS['accent_dark'],
            cursor='hand2', command=self._attempt_login
        ).pack(fill='x', ipady=8)

        # Tab order — pressing Tab moves focus from username to password.
        # Returns 'break' to prevent Tkinter's default Tab handler from
        # also firing and jumping focus to an unintended widget.
        self.username_entry.bind(
            '<Tab>',
            lambda e: self.password_entry.focus() or 'break'
        )

        # Bind Enter key so the user does not have to click the button
        self.master.bind('<Return>', lambda e: self._attempt_login())

        # Set focus to username field on load so the user can type immediately
        self.username_entry.focus()

    def _attempt_login(self) -> None:
        """Read the form fields and call the auth login function."""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        result = login(username, password)

        if result['success']:
            # Unbind Enter before navigating — leaving it active
            # would cause it to fire unexpectedly on the next screen.
            self.master.unbind('<Return>')
            self.master.show_dashboard()
        else:
            # Show the error, clear the password field and return focus
            # to the password entry so the user can try again immediately.
            self.error_var.set(result['message'])
            self.password_var.set('')
            self.password_entry.focus()