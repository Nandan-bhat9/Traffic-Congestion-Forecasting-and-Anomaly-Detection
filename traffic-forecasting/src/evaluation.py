"""
evaluation.py
-------------
Compute MAE, RMSE (and optionally MAPE) for model predictions.
"""

import numpy as np
import pandas as pd


def compute_metrics(actual: pd.Series, predicted: pd.Series) -> dict:
    """
    Align actual and predicted on their shared index, then compute metrics.
    """
    common_idx = actual.index.intersection(predicted.index)
    a = actual.loc[common_idx].values
    p = predicted.loc[common_idx].values

    mae  = np.mean(np.abs(a - p))
    rmse = np.sqrt(np.mean((a - p) ** 2))

    metrics = {'MAE': round(mae, 4), 'RMSE': round(rmse, 4), 'n': len(common_idx)}

    # MAPE only if no zero/near-zero actuals
    if np.all(np.abs(a) > 0.1):
        mape = np.mean(np.abs((a - p) / a)) * 100
        metrics['MAPE_%'] = round(mape, 2)

    return metrics
