"""
arima_model.py
--------------
Simple ARIMA model for traffic forecasting using statsmodels.
"""

import time
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')


def train_arima(train_series: pd.Series, test_series: pd.Series, order=(2, 1, 2)):
    """
    Fit ARIMA on train_series and produce forecasts for the test period.

    Returns
    -------
    predictions : pd.Series  — aligned with test_series index
    train_time  : float      — seconds taken to fit
    """
    print(f"[arima] Fitting ARIMA{order} on {len(train_series)} training points …")
    t0 = time.time()

    model = ARIMA(train_series, order=order)
    fitted = model.fit()

    train_time = time.time() - t0
    print(f"[arima] Fitted in {train_time:.1f}s")

    # Forecast
    n_forecast = len(test_series)
    forecast = fitted.forecast(steps=n_forecast)
    predictions = pd.Series(forecast.values, index=test_series.index, name='arima_pred')

    print(f"[arima] Forecasted {n_forecast} steps.")
    return predictions, train_time
