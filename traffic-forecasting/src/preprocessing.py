"""
preprocessing.py
----------------
Clean and prepare the raw traffic dataset.
"""

import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
PROCESSED_FILE = os.path.join(PROCESSED_DIR, 'traffic_clean.csv')


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Steps:
      1. Parse timestamps.
      2. Sort chronologically.
      3. Select one representative sensor.
      4. Handle missing values with linear interpolation.
      5. Remove duplicates.
      6. Rename traffic column to 'traffic'.
      7. Set timestamp as index.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    print("[preprocessing] Starting preprocessing …")

    # --- 1. Ensure datetime ---
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    # --- 2. Sort chronologically ---
    df = df.sort_values('timestamp').reset_index(drop=True)

    # --- 3. Select one sensor ---
    if 'sensor_id' in df.columns:
        sensor = df['sensor_id'].value_counts().idxmax()
        print(f"[preprocessing] Selected sensor: {sensor}")
        df = df[df['sensor_id'] == sensor].copy()

    # --- 4. Keep only timestamp + traffic column ---
    traffic_col = 'traffic'
    df = df[['timestamp', traffic_col]].copy()

    # --- 5. Set index ---
    df = df.set_index('timestamp')

    # --- 6. Remove duplicates ---
    df = df[~df.index.duplicated(keep='first')]

    # --- 7. Reindex to fill gaps (5-min frequency) and interpolate ---
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq='5min')
    df = df.reindex(full_idx)
    df.index.name = 'timestamp'
    missing_before = df['traffic'].isna().sum()
    df['traffic'] = df['traffic'].interpolate(method='linear')
    df['traffic'] = df['traffic'].bfill()
    df['traffic'] = df['traffic'].ffill()
    print(f"[preprocessing] Filled {missing_before} missing value(s) via interpolation.")

    # --- 8. Save processed data ---
    df.to_csv(PROCESSED_FILE)
    print(f"[preprocessing] Saved cleaned data to {PROCESSED_FILE}")
    print(f"[preprocessing] Shape: {df.shape}  |  Date range: {df.index.min()} → {df.index.max()}")

    return df
