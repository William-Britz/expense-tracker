# gui/app.py
# Author  : William
# Version : 1.1
#
# Root application controller. Creates the main Tkinter window,
# defines the global colour scheme and font constants, and handles
# navigation between screens by swapping frames in and out.
#
# No business logic lives here. This file only controls the window
# and routes the user to the correct screen.

import tkinter as tk


# ── Colour scheme ────────────────────────────────────────────────────────────
# Defined once here and imported by every GUI module.
# Changing a colour here changes it everywhere in the application.
COLORS = {
    'bg':          '#0f1923',
    'panel':       '#1a2a3a',
    'accent':      '#1bb0ce',
    'accent_dark': '#1490aa',
    'text':        '#e8edf2',
    'text_dim':    '#8a9bb0',
    'entry_bg':    '#243447',
    'success':     '#2ecc71',
    'error':       '#e74c3c',
    'row_alt':     '#1f3145',
}

# ── Font scheme ───────────────────────────────────────────────────────────────
# Tuples of (font family, size, weight).
# Arial is used throughout — available on all platforms without installation.
FONTS = {
    'title':   ('Arial', 18, 'bold'),
    'heading': ('Arial', 13, 'bold'),
    'body':    ('Arial', 11),
    'small':   ('Arial', 9),
    'code':    ('Courier New', 10),
}


class App(tk.Tk):
    """
    Main application window. Inherits from tk.Tk which is the root window.

    The App class owns one frame at a time — the current screen.
    show_frame() destroys the current screen and replaces it with a new one.
    This is the standard pattern for multi-screen Tkinter applications.

    Navigation methods are defined here so any screen can navigate to any
    other screen by calling self.master.<method>.
    """

    def __init__(self):
        super().__init__()
        self.title("ExpenseTracker")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self.configure(bg=COLORS['bg'])
        self.resizable(True, True)
        self._current_frame = None

        # Handle the window close button cleanly.
        # Without this, clicking X while a database operation is in
        # progress can leave connections open or throw errors on exit.
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.show_login()

    def _on_close(self) -> None:
        """Called when the user clicks the window close button."""
        self.destroy()

    def show_frame(self, FrameClass, **kwargs) -> None:
        """
        Destroy the current screen and display a new one.
        FrameClass is the class of the screen to show.
        kwargs are passed to the screen constructor (e.g. expense_id for edit mode).
        """
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = FrameClass(self, **kwargs)
        self._current_frame.pack(fill='both', expand=True)

    def show_login(self) -> None:
        # Deferred import — only loads LoginScreen when this method is called.
        # Avoids loading all screens at startup and prevents circular imports.
        from gui.login_screen import LoginScreen
        self.show_frame(LoginScreen)

    def show_dashboard(self) -> None:
        from gui.dashboard import Dashboard
        self.show_frame(Dashboard)

    def show_add_expense(self, expense_id=None) -> None:
        from gui.expense_form import ExpenseForm
        self.show_frame(ExpenseForm, expense_id=expense_id)

    def show_reports(self) -> None:
        from gui.reports_screen import ReportsScreen
        self.show_frame(ReportsScreen)