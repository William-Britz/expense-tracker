# gui/reports_screen.py
# Author  : William
# Version : 1.1
#
# Reports and charts screen. Embeds two Matplotlib charts directly
# in the Tkinter window using the TkAgg backend.
# Calls logic/expenses.py for data — no SQL here.

import tkinter as tk
from gui.app import COLORS, FONTS
from logic.expenses import get_expenses
from charts.charts import build_pie_chart, build_bar_chart


class ReportsScreen(tk.Frame):
    """
    Reports screen. Inherits from tk.Frame so it can be
    managed by App.show_frame() like any other screen.
    """

    def __init__(self, master):
        super().__init__(master, bg=COLORS['bg'])
        self._build()
        # Escape key returns to the dashboard — consistent with other screens
        self.master.bind('<Escape>', lambda e: self._back())

    def _build(self) -> None:
        """Build and place all widgets for the reports screen."""

        # ── Top bar ───────────────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=COLORS['panel'], height=50)
        topbar.pack(fill='x')
        topbar.pack_propagate(False)

        tk.Label(
            topbar, text="  Reports & Charts",
            font=FONTS['heading'], bg=COLORS['panel'], fg=COLORS['accent']
        ).pack(side='left', padx=10)

        tk.Button(
            topbar, text="Back to Dashboard",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['accent'],
            relief='flat', cursor='hand2',
            command=self._back
        ).pack(side='right', padx=16)

        tk.Button(
            topbar, text="Refresh",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim'],
            relief='flat', cursor='hand2',
            command=self._refresh
        ).pack(side='right', padx=8)

        # ── Chart container ───────────────────────────────────────────────────
        # Stored as an instance variable so _refresh() can destroy
        # and rebuild it without rebuilding the entire screen.
        self.chart_area = tk.Frame(self, bg=COLORS['bg'])
        self.chart_area.pack(fill='both', expand=True, padx=20, pady=16)

        # ── Summary bar ───────────────────────────────────────────────────────
        self.summary_frame = tk.Frame(self, bg=COLORS['panel'])
        self.summary_frame.pack(fill='x', padx=20, pady=(0, 16))

        self._render_charts()

    def _render_charts(self) -> None:
        """
        Build and embed both charts and update the summary totals.
        Called on first load and again on refresh.
        Destroys existing chart widgets before rebuilding so stale
        charts do not stack up in memory on repeated refreshes.
        """
        # Clear existing chart widgets before rebuilding
        for widget in self.chart_area.winfo_children():
            widget.destroy()
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        # Pie chart — left side
        pie_frame = tk.Frame(
            self.chart_area, bg=COLORS['panel'], padx=8, pady=8
        )
        pie_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        try:
            pie_canvas = build_pie_chart(pie_frame)
            pie_canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            tk.Label(
                pie_frame, text=f"Chart error: {str(e)}",
                font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['error']
            ).pack(expand=True)

        # Bar chart — right side
        bar_frame = tk.Frame(
            self.chart_area, bg=COLORS['panel'], padx=8, pady=8
        )
        bar_frame.pack(side='left', fill='both', expand=True)

        try:
            bar_canvas = build_bar_chart(bar_frame)
            bar_canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            tk.Label(
                bar_frame, text=f"Chart error: {str(e)}",
                font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['error']
            ).pack(expand=True)

        # Summary totals
        expenses = get_expenses()
        total    = sum(e['amount'] for e in expenses)
        count    = len(expenses)

        tk.Label(
            self.summary_frame,
            text=f"  Total Expenses: {count}   |   Total Spent: R {total:.2f}  ",
            font=FONTS['body'], bg=COLORS['panel'], fg=COLORS['text']
        ).pack(side='left', padx=12, pady=8)

        tk.Label(
            self.summary_frame,
            text="Right-click a chart to save it as an image  ",
            font=FONTS['small'], bg=COLORS['panel'], fg=COLORS['text_dim']
        ).pack(side='right', padx=12, pady=8)

    def _refresh(self) -> None:
        """Rebuild charts and summary from fresh database data."""
        self._render_charts()

    def _back(self) -> None:
        """Unbind Escape and return to the dashboard."""
        self.master.unbind('<Escape>')
        self.master.show_dashboard()