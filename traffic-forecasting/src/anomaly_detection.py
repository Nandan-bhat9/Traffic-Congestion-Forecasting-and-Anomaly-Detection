"""
anomaly_detection.py
--------------------
Detect unusual traffic observations using forecasting error thresholding.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

PLOTS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'plots')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'results')

sns.set_theme(style='darkgrid', palette='muted')


def detect_anomalies(actual: pd.Series, predicted: pd.Series,
                     label: str = 'Model') -> pd.DataFrame:
    """
    Use mean + 3Ïƒ error threshold to flag unusual traffic observations.

    Returns a DataFrame of anomaly records.
    """
    # Align on common index
    common_idx = actual.index.intersection(predicted.index)
    a = actual.loc[common_idx]
    p = predicted.loc[common_idx]

    error = (a - p).abs()
    threshold = error.mean() + 3 * error.std()

    anomaly_mask = error > threshold
    anomalies = pd.DataFrame({
        'timestamp':  common_idx[anomaly_mask],
        'traffic':    a.values[anomaly_mask],
        'prediction': p.values[anomaly_mask],
        'error':      error.values[anomaly_mask],
    })

    total = len(common_idx)
    n_anom = anomaly_mask.sum()
    pct = round(n_anom / total * 100, 2)

    print(f"[anomaly] Threshold: {threshold:.4f}")
    print(f"[anomaly] Total observations: {total}  |  Anomalies: {n_anom}  ({pct}%)")

    # â”€â”€ Visualization â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(a.index, a.values, color='steelblue', linewidth=0.8,
            label='Actual Traffic', alpha=0.8)
    ax.plot(p.index, p.values, color='seagreen', linewidth=0.8,
            linestyle='--', label=f'{label} Prediction', alpha=0.7)

    if n_anom > 0:
        ax.scatter(
            common_idx[anomaly_mask],
            a.values[anomaly_mask],
            color='tomato', zorder=5, s=50,
            label=f'Unusual Observations ({n_anom})'
        )

    ax.set_title(f'Anomaly Detection â€” {label}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time')
    ax.set_ylabel('Traffic')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()

    os.makedirs(PLOTS_DIR, exist_ok=True)
    fig.savefig(os.path.join(PLOTS_DIR, 'anomalies.png'), bbox_inches='tight')
    plt.close(fig)
    print("  [anomaly] Saved anomalies.png")

    # â”€â”€ Save CSV â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    os.makedirs(RESULTS_DIR, exist_ok=True)
    anom_path = os.path.join(RESULTS_DIR, 'anomalies.csv')
    anomalies.to_csv(anom_path, index=False)
    print(f"  [anomaly] Saved anomalies.csv  ({n_anom} records)")

    return anomalies, {
        'total': total, 'n_anomalies': int(n_anom), 'pct': pct,
        'threshold': round(float(threshold), 4)
    }

