import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd

from utils import (
    merge_team_data,
    get_best_worst_team_pitchers,
    WIN_RATE_LABELS,
    ERA_LABELS,
    ERA_BINS,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUT_DIR, exist_ok=True)


# ─── Q1: Line Plot ────────────────────────────────────────────────────────────

def plot_q1_line(df):
    data = df.dropna(subset=['win_rate', 'AVG']).sort_values('win_rate').reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data['win_rate'], data['AVG'], color='steelblue', linewidth=1.2, alpha=0.8)
    ax.scatter(data['win_rate'], data['AVG'], color='steelblue', s=18, zorder=3)

    ax.set_xlabel('Team Winning Rate (sorted lowest to highest)', fontsize=12)
    ax.set_ylabel('Team Batting Average (AVG)', fontsize=12)
    ax.set_title('Team Winning Rate vs. Team Batting Average (2003–2023)', fontsize=14)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.3f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.3f'))
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'q1_line_plot.png')
    plt.savefig(out, dpi=150)
    plt.close()
    print(f'Saved: {out}')


# ─── Q1: Violin Plot ──────────────────────────────────────────────────────────

def plot_q1_violin(df):
    data = df.dropna(subset=['win_rate_bin', 'AVG']).copy()
    data['win_rate_bin'] = data['win_rate_bin'].astype(str)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(
        data=data,
        x='win_rate_bin',
        y='AVG',
        hue='win_rate_bin',
        order=WIN_RATE_LABELS,
        hue_order=WIN_RATE_LABELS,
        palette='Blues',
        inner='box',
        legend=False,
        ax=ax,
    )

    ax.set_xlabel('Team Winning Rate Interval', fontsize=12)
    ax.set_ylabel('Team Batting Average (AVG)', fontsize=12)
    ax.set_title('Distribution of Team Batting Average by Winning Rate Interval (2003–2023)', fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.3f'))
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'q1_violin_plot.png')
    plt.savefig(out, dpi=150)
    plt.close()
    print(f'Saved: {out}')


# ─── Q2: Bar Plot ─────────────────────────────────────────────────────────────

def plot_q2_bar(df):
    data = df.dropna(subset=['win_rate_bin'])
    hr_by_bin = data.groupby('win_rate_bin', observed=False)['HR'].sum().reindex(WIN_RATE_LABELS)

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(WIN_RATE_LABELS, hr_by_bin.values, color='steelblue', edgecolor='white', width=0.6)

    for bar, val in zip(bars, hr_by_bin.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f'{int(val):,}', ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Team Winning Rate Interval', fontsize=12)
    ax.set_ylabel('Total Home Runs (HR)', fontsize=12)
    ax.set_title('Total Home Runs by Team Winning Rate Interval (2003–2023)', fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, 'q2_bar_plot.png')
    plt.savefig(out, dpi=150)
    plt.close()
    print(f'Saved: {out}')


# ─── Q3: Histograms ───────────────────────────────────────────────────────────

def _era_counts(df):
    counts = df['era_bin'].value_counts().reindex(ERA_LABELS, fill_value=0)
    return counts


def plot_q3_histograms(best_df, worst_df):
    best_counts = _era_counts(best_df)
    worst_counts = _era_counts(worst_df)

    for label, counts, color, fname in [
        ('Highest Winning Rate Teams', best_counts, 'steelblue', 'q3_histogram_best.png'),
        ('Lowest Winning Rate Teams', worst_counts, 'tomato', 'q3_histogram_worst.png'),
    ]:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(ERA_LABELS, counts.values, color=color, edgecolor='white', width=0.8)

        for i, val in enumerate(counts.values):
            if val > 0:
                ax.text(i, val + 0.3, str(val), ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('ERA Range', fontsize=12)
        ax.set_ylabel('Number of Pitchers', fontsize=12)
        ax.set_title(f'ERA Distribution — {label} (2003–2023)', fontsize=13)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()

        out = os.path.join(OUT_DIR, fname)
        plt.savefig(out, dpi=150)
        plt.close()
        print(f'Saved: {out}')


# ─── Q4: Pie Charts ───────────────────────────────────────────────────────────

def plot_q4_pie(best_df, worst_df):
    best_counts = _era_counts(best_df)
    worst_counts = _era_counts(worst_df)

    for label, counts, fname in [
        ('Highest Winning Rate Teams', best_counts, 'q4_pie_best.png'),
        ('Lowest Winning Rate Teams', worst_counts, 'q4_pie_worst.png'),
    ]:
        nonzero = counts[counts > 0]

        fig, ax = plt.subplots(figsize=(9, 7))
        wedges, texts, autotexts = ax.pie(
            nonzero.values,
            labels=nonzero.index,
            autopct='%1.1f%%',
            startangle=140,
            pctdistance=0.82,
            colors=plt.cm.tab20.colors[:len(nonzero)],
        )
        for at in autotexts:
            at.set_fontsize(9)
        ax.set_title(f'ERA Distribution (Proportion) — {label}\n(2003–2023)', fontsize=13)

        plt.tight_layout()
        out = os.path.join(OUT_DIR, fname)
        plt.savefig(out, dpi=150)
        plt.close()
        print(f'Saved: {out}')


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('Loading data...')
    team_df = merge_team_data()
    best_df, worst_df = get_best_worst_team_pitchers()

    print(f'  Team records: {len(team_df)}')
    print(f'  Best-team pitchers: {len(best_df)}')
    print(f'  Worst-team pitchers: {len(worst_df)}')
    print()

    print('Q1 — Line plot...')
    plot_q1_line(team_df)

    print('Q1 — Violin plot...')
    plot_q1_violin(team_df)

    print('Q2 — Bar plot...')
    plot_q2_bar(team_df)

    print('Q3 — Histograms...')
    plot_q3_histograms(best_df, worst_df)

    print('Q4 — Pie charts...')
    plot_q4_pie(best_df, worst_df)

    print('\nAll charts saved to:', OUT_DIR)
