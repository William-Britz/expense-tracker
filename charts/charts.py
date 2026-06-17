# charts/charts.py
# Author  : William
# Version : 1.1
#
# Matplotlib chart builders for the reports screen.
# Each function builds one chart, embeds it into a Tkinter parent frame
# and returns the FigureCanvasTkAgg widget for the caller to pack.
#
# matplotlib.use('TkAgg') must be called before importing pyplot.
# TkAgg is the backend that renders Matplotlib figures inside Tkinter windows.
# If this is not set first, Matplotlib picks a default backend that has no
# Tkinter integration and the charts cannot be embedded in the application.

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logic.expenses import get_summary_by_category, get_monthly_totals


# ── Chart colour palette ──────────────────────────────────────────────────────
# Defined locally so charts.py has no dependency on gui/app.py.
# Background colours match the application dark theme.

CHART_COLORS = [
    '#1bb0ce', '#2ecc71', '#e67e22', '#9b59b6',
    '#e74c3c', '#1abc9c', '#f39c12', '#3498db',
    '#fd79a8', '#a29bfe', '#55efc4', '#fdcb6e',
]

BG  = '#1a2a3a'   # panel background
FG  = '#e8edf2'   # text and axis colour
DIM = '#8a9bb0'   # secondary text


def build_pie_chart(parent_frame) -> FigureCanvasTkAgg:
    """
    Build a pie chart showing total spending by category.
    Embeds the chart into parent_frame and returns the canvas widget.

    The caller is responsible for calling .get_tk_widget().pack()
    on the returned canvas to make it visible.

    plt.close(fig) is called after creating the canvas to release
    the figure from Matplotlib's internal figure manager. Without this,
    each refresh call creates a new figure that is never garbage collected,
    causing memory to accumulate over the application's lifetime.
    """
    data = get_summary_by_category()

    fig, ax = plt.subplots(figsize=(5.2, 4), facecolor=BG)
    ax.set_facecolor(BG)

    if not data:
        ax.text(
            0.5, 0.5, 'No expense data yet',
            ha='center', va='center',
            color=DIM, fontsize=12, transform=ax.transAxes
        )
    else:
        labels  = [d['category'] for d in data]
        amounts = [d['total']    for d in data]
        colors  = CHART_COLORS[:len(labels)]

        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'color': FG, 'fontsize': 9}
        )

        # Make percentage labels readable against the wedge colours
        for autotext in autotexts:
            autotext.set_color(BG)
            autotext.set_fontweight('bold')

    ax.set_title('Spending by Category', color=FG, fontsize=12, pad=14)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()

    # Release figure from Matplotlib's figure manager to prevent memory leaks
    plt.close(fig)

    return canvas


def build_bar_chart(parent_frame) -> FigureCanvasTkAgg:
    """
    Build a bar chart showing total spending per month.
    Embeds the chart into parent_frame and returns the canvas widget.

    The caller is responsible for calling .get_tk_widget().pack()
    on the returned canvas to make it visible.

    plt.close(fig) called after canvas creation — same reason as pie chart.
    """
    data = get_monthly_totals()

    fig, ax = plt.subplots(figsize=(5.2, 4), facecolor=BG)
    ax.set_facecolor(BG)

    if not data:
        ax.text(
            0.5, 0.5, 'No expense data yet',
            ha='center', va='center',
            color=DIM, fontsize=12, transform=ax.transAxes
        )
    else:
        months  = [d['month'] for d in data]
        totals  = [d['total'] for d in data]
        max_val = max(totals) if totals else 0

        bars = ax.bar(
            months, totals,
            color=CHART_COLORS[0],
            edgecolor=BG,
            width=0.5
        )

        # X axis labels
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(
            months, rotation=45, ha='right', color=FG, fontsize=8
        )

        # Y axis
        ax.tick_params(axis='y', colors=FG)
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f'R{x:,.0f}')
        )

        # Remove top and right spines — cleaner look on dark background
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(FG)
        ax.spines['left'].set_color(FG)

        # Value labels above each bar.
        # Offset is 1% of the tallest bar so labels scale with the data.
        # max_val defaults to 0 if totals is empty — prevents ValueError.
        offset = max_val * 0.01 if max_val > 0 else 1

        for bar, total in zip(bars, totals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + offset,
                f'R{total:,.0f}',
                ha='center', va='bottom',
                color=FG, fontsize=8
            )

    ax.set_title('Monthly Spending', color=FG, fontsize=12, pad=14)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()

    plt.close(fig)

    return canvas