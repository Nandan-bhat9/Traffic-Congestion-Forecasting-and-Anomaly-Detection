"""
data_loader.py
--------------
Downloads or generates the traffic dataset.
Uses a synthetic but realistic traffic dataset if METR-LA is unavailable.
"""

import os
import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
DATA_FILE = os.path.join(RAW_DIR, 'traffic_data.csv')


def _generate_synthetic_traffic(n_days: int = 60) -> pd.DataFrame:
    """
    Generate a synthetic traffic time-series that mimics real sensor data.
    5-minute intervals, with realistic daily/weekly patterns + noise.
    """
    np.random.seed(42)
    periods = n_days * 24 * 12          # 5-min intervals
    idx = pd.date_range('2024-01-01', periods=periods, freq='5min')

    hour = idx.hour
    dow  = idx.dayofweek                # 0=Mon … 6=Sun

    # Base daily pattern: two peaks (morning rush & evening rush)
    morning_peak = np.exp(-((hour - 8) ** 2) / 4)
    evening_peak = np.exp(-((hour - 17) ** 2) / 4)
    daily_pattern = 40 + 30 * morning_peak + 25 * evening_peak

    # Weekend dampening
    weekend_factor = np.where(dow >= 5, 0.55, 1.0)

    # Noise
    noise = np.random.normal(0, 4, size=len(idx))

    traffic = daily_pattern * weekend_factor + noise
    traffic = np.clip(traffic, 0, None)          # no negative traffic

    df = pd.DataFrame({'timestamp': idx, 'sensor_id': 'sensor_001', 'traffic': traffic})
    return df


def load_data() -> pd.DataFrame:
    """
    Load traffic data. If the file already exists, load it directly.
    Otherwise generate a synthetic dataset and save it.
    """
    os.makedirs(RAW_DIR, exist_ok=True)

    if os.path.exists(DATA_FILE):
        print(f"[data_loader] Dataset found — loading from {DATA_FILE}")
        df = pd.read_csv(DATA_FILE, parse_dates=['timestamp'])
    else:
        print("[data_loader] Dataset not found — generating synthetic traffic data …")
        df = _generate_synthetic_traffic(n_days=60)
        df.to_csv(DATA_FILE, index=False)
        print(f"[data_loader] Saved to {DATA_FILE}")

    return df
