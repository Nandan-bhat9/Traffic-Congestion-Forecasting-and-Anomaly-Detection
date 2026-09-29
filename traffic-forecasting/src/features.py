"""
features.py
-----------
Extract time-series features: time, lag, and rolling features.
"""

import pandas as pd
import numpy as np


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add temporal, lag, and rolling features to the traffic dataframe.
    Returns a copy with no NaN rows (dropped after lag creation).
    """
    print("[features] Extracting features …")

    feat = df.copy()

    # -- Time features ---------------------------------------------------
    feat['hour']       = feat.index.hour
    feat['day_of_week'] = feat.index.dayofweek
    feat['is_weekend'] = (feat['day_of_week'] >= 5).astype(int)

    # -- Lag features (5-min steps) --------------------------------------
    feat['lag_1'] = feat['traffic'].shift(1)
    feat['lag_3'] = feat['traffic'].shift(3)
    feat['lag_6'] = feat['traffic'].shift(6)

    # -- Rolling features ------------------------------------------------
    feat['rolling_mean'] = feat['traffic'].rolling(window=6).mean()
    feat['rolling_std']  = feat['traffic'].rolling(window=6).std()

    # Drop rows that have NaN due to lag/rolling
    feat = feat.dropna()

    print(f"[features] Feature set shape after dropping NaN rows: {feat.shape}")
    print(f"[features] Columns: {list(feat.columns)}")

    return feat
