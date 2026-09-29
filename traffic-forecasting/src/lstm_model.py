"""
lstm_model.py
-------------
Small LSTM model for traffic forecasting using TensorFlow/Keras.
"""

import os
import time
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'   # suppress TF info logs

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


SEQUENCE_LENGTH = 12    # 12 × 5-min = 1 hour look-back
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')


def _make_sequences(series: np.ndarray, seq_len: int):
    X, y = [], []
    for i in range(seq_len, len(series)):
        X.append(series[i - seq_len:i])
        y.append(series[i])
    return np.array(X), np.array(y)


def train_lstm(train_series: pd.Series, test_series: pd.Series):
    """
    Train a small LSTM and return predictions aligned with test_series.

    Returns
    -------
    predictions : pd.Series  — aligned with test_series index
    train_time  : float      — seconds taken to fit
    history     : History    — Keras training history
    """
    print(f"[lstm] Preparing sequences (seq_len={SEQUENCE_LENGTH}) …")

    # Normalize using training stats only
    mean = train_series.mean()
    std  = train_series.std()

    train_norm = (train_series.values - mean) / std
    test_norm  = (test_series.values  - mean) / std

    # Build full sequence set from combined series (to generate test seqs)
    combined = np.concatenate([train_norm, test_norm])
    X_all, y_all = _make_sequences(combined, SEQUENCE_LENGTH)

    n_train_seq = len(train_norm) - SEQUENCE_LENGTH
    X_train, y_train = X_all[:n_train_seq], y_all[:n_train_seq]
    X_test,  y_test  = X_all[n_train_seq:], y_all[n_train_seq:]

    # Reshape for LSTM: (samples, timesteps, features)
    X_train = X_train.reshape(-1, SEQUENCE_LENGTH, 1)
    X_test  = X_test.reshape(-1, SEQUENCE_LENGTH, 1)

    print(f"[lstm] Train sequences: {X_train.shape}  Test sequences: {X_test.shape}")

    # -- Model -----------------------------------------------------------
    model = Sequential([
        LSTM(32, input_shape=(SEQUENCE_LENGTH, 1)),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    early_stop = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)

    t0 = time.time()
    history = model.fit(
        X_train, y_train,
        epochs=15,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1
    )
    train_time = time.time() - t0
    print(f"[lstm] Trained in {train_time:.1f}s  |  epochs run: {len(history.history['loss'])}")

    # -- Save model ------------------------------------------------------
    os.makedirs(MODELS_DIR, exist_ok=True)
    model.save(os.path.join(MODELS_DIR, 'lstm_model.keras'))

    # -- Predict ---------------------------------------------------------
    preds_norm = model.predict(X_test, verbose=0).flatten()
    preds = preds_norm * std + mean   # denormalize

    # Align with test_series index (SEQUENCE_LENGTH offsets exist)
    idx_offset = len(test_series) - len(preds)
    pred_index = test_series.index[idx_offset:]
    predictions = pd.Series(preds, index=pred_index, name='lstm_pred')

    return predictions, train_time, history
