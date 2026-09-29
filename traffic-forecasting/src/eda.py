"""
eda.py
------
Exploratory Data Analysis â€” generates 5 graphs and a text summary.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

PLOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'plots')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'results')

sns.set_theme(style='darkgrid', palette='muted')
plt.rcParams['figure.dpi'] = 100


def _save(fig, name: str):
    os.makedirs(PLOTS_DIR, exist_ok=True)
    path = os.path.join(PLOTS_DIR, name)
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  [eda] Saved {name}")


def run_eda(df: pd.DataFrame) -> dict:
    """Run all EDA steps and return a findings dict."""
    print("[eda] Running exploratory data analysis â€¦")

    findings = {}

    # â”€â”€ Graph 1: Traffic over time â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df.index, df['traffic'], color='steelblue', linewidth=0.6, alpha=0.8)
    ax.set_title('Traffic Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Traffic (speed / count)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    _save(fig, 'traffic_over_time.png')

    # â”€â”€ Graph 2: Distribution histogram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df['traffic'], bins=50, color='steelblue', edgecolor='white', alpha=0.85)
    ax.set_title('Traffic Value Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Traffic')
    ax.set_ylabel('Frequency')
    _save(fig, 'traffic_distribution.png')

    # â”€â”€ Graph 3: Average traffic by hour â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    df_temp = df.copy()
    df_temp['hour'] = df_temp.index.hour
    hourly = df_temp.groupby('hour')['traffic'].mean()
    peak_hour = int(hourly.idxmax())
    findings['peak_hour'] = peak_hour
    findings['peak_hour_traffic'] = round(hourly.max(), 2)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(hourly.index, hourly.values, color='steelblue', alpha=0.85)
    ax.axvline(peak_hour, color='tomato', linestyle='--', label=f'Peak: {peak_hour}:00')
    ax.set_title('Average Traffic by Hour of Day', fontsize=14, fontweight='bold')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Average Traffic')
    ax.legend()
    _save(fig, 'hourly_traffic.png')

    # â”€â”€ Graph 4: Average traffic by day of week â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    df_temp['dow'] = df_temp.index.dayofweek
    daily = df_temp.groupby('dow')['traffic'].mean()
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekend_avg = daily[[5, 6]].mean()
    weekday_avg = daily[[0, 1, 2, 3, 4]].mean()
    findings['weekday_avg'] = round(weekday_avg, 2)
    findings['weekend_avg'] = round(weekend_avg, 2)

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ['#2196F3' if i < 5 else '#FF7043' for i in range(7)]
    ax.bar(day_names, daily.values, color=colors, alpha=0.85)
    ax.set_title('Average Traffic by Day of Week', fontsize=14, fontweight='bold')
    ax.set_xlabel('Day')
    ax.set_ylabel('Average Traffic')
    import matplotlib.patches as mpatches
    wk = mpatches.Patch(color='#2196F3', label='Weekday')
    we = mpatches.Patch(color='#FF7043', label='Weekend')
    ax.legend(handles=[wk, we])
    _save(fig, 'daily_traffic.png')

    # â”€â”€ Graph 5: Rolling average â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    rolling = df['traffic'].rolling(window=72).mean()   # 72 Ã— 5min = 6h window
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df.index, df['traffic'], color='steelblue', linewidth=0.5, alpha=0.5, label='Actual')
    ax.plot(df.index, rolling, color='tomato', linewidth=1.5, label='6-h Rolling Mean')
    ax.set_title('Traffic with Rolling Average (6-hour window)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Traffic')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    _save(fig, 'rolling_average.png')

    # â”€â”€ Statistical summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    findings['mean_traffic'] = round(df['traffic'].mean(), 2)
    findings['std_traffic'] = round(df['traffic'].std(), 2)
    findings['min_traffic'] = round(df['traffic'].min(), 2)
    findings['max_traffic'] = round(df['traffic'].max(), 2)
    findings['cv_pct'] = round(df['traffic'].std() / df['traffic'].mean() * 100, 1)

    # â”€â”€ Save findings text â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    os.makedirs(RESULTS_DIR, exist_ok=True)
    txt_path = os.path.join(RESULTS_DIR, 'eda_findings.txt')
    with open(txt_path, 'w') as f:
        f.write("=" * 55 + "\n")
        f.write("  EDA FINDINGS â€” Traffic Congestion Mini-Project\n")
        f.write("=" * 55 + "\n\n")
        f.write(f"Dataset shape           : {df.shape}\n")
        f.write(f"Date range              : {df.index.min()} â†’ {df.index.max()}\n\n")
        f.write(f"Mean traffic            : {findings['mean_traffic']}\n")
        f.write(f"Std deviation           : {findings['std_traffic']}\n")
        f.write(f"Min traffic             : {findings['min_traffic']}\n")
        f.write(f"Max traffic             : {findings['max_traffic']}\n")
        f.write(f"Coefficient of variation: {findings['cv_pct']}%\n\n")
        f.write(f"Peak hour               : {findings['peak_hour']}:00  "
                f"(avg traffic = {findings['peak_hour_traffic']})\n")
        f.write(f"Weekday avg traffic     : {findings['weekday_avg']}\n")
        f.write(f"Weekend avg traffic     : {findings['weekend_avg']}\n\n")
        f.write("Key observations:\n")
        f.write("  - Traffic exhibits clear daily periodicity with peak hours.\n")
        f.write(f"  - Weekend traffic is {'lower' if weekend_avg < weekday_avg else 'higher'} "
                f"than weekday traffic.\n")
        f.write("  - Rolling averages reveal a smooth underlying trend.\n")
        f.write("  - Short-term fluctuations exist around the trend.\n")
    print(f"  [eda] Saved eda_findings.txt")

    return findings

