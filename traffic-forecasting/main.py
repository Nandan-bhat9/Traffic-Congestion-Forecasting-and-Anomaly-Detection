"""
main.py
-------
Traffic Congestion Forecasting and Anomaly Detection â€” Mini Project
Run: python main.py
"""

import os
import sys
import warnings
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

warnings.filterwarnings('ignore')

# â”€â”€ Add src to path â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader       import load_data
from preprocessing     import preprocess
from eda               import run_eda
from features          import extract_features
from arima_model       import train_arima
from lstm_model        import train_lstm
from evaluation        import compute_metrics
from anomaly_detection import detect_anomalies

PLOTS_DIR   = os.path.join(os.path.dirname(__file__), 'outputs', 'plots')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'outputs', 'results')

sns.set_theme(style='darkgrid', palette='muted')


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    print("\n" + "=" * 60)
    print("  Traffic Congestion Forecasting & Anomaly Detection")
    print("=" * 60 + "\n")

    # â”€â”€ Step 1: Load data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("â”€â”€ Step 1: Loading Data â”€â”€")
    raw_df = load_data()

    # â”€â”€ Step 2: Preprocess â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 2: Preprocessing â”€â”€")
    df = preprocess(raw_df)

    # â”€â”€ Step 3 & 4: EDA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 3 & 4: Exploratory Data Analysis â”€â”€")
    eda_findings = run_eda(df)

    # â”€â”€ Step 5: Feature extraction â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 5: Feature Extraction â”€â”€")
    feat_df = extract_features(df)

    # â”€â”€ Step 6: Train/test split (80/20, no shuffle) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 6: Train/Test Split (80/20) â”€â”€")
    traffic = df['traffic']
    split_idx = int(len(traffic) * 0.80)
    train_series = traffic.iloc[:split_idx]
    test_series  = traffic.iloc[split_idx:]
    print(f"  Train: {len(train_series)} pts  |  Test: {len(test_series)} pts")

    # â”€â”€ Step 7: ARIMA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 7: ARIMA Model â”€â”€")
    arima_preds, arima_time = train_arima(train_series, test_series, order=(2, 1, 2))

    # â”€â”€ Step 8: LSTM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 8: LSTM Model â”€â”€")
    lstm_preds, lstm_time, lstm_history = train_lstm(train_series, test_series)

    # â”€â”€ Step 9: Evaluation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 9: Model Evaluation â”€â”€")
    arima_metrics = compute_metrics(test_series, arima_preds)
    lstm_metrics  = compute_metrics(test_series, lstm_preds)

    print(f"\n  ARIMA  â†’ MAE: {arima_metrics['MAE']}  RMSE: {arima_metrics['RMSE']}")
    print(f"  LSTM   â†’ MAE: {lstm_metrics['MAE']}   RMSE: {lstm_metrics['RMSE']}")

    # â”€â”€ Step 10: Model comparison table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 10: Model Comparison â”€â”€")
    comparison = pd.DataFrame([
        {
            'Model': 'ARIMA',
            'MAE':   arima_metrics['MAE'],
            'RMSE':  arima_metrics['RMSE'],
            'Training_Time_s': round(arima_time, 2)
        },
        {
            'Model': 'LSTM',
            'MAE':   lstm_metrics['MAE'],
            'RMSE':  lstm_metrics['RMSE'],
            'Training_Time_s': round(lstm_time, 2)
        },
    ])
    print("\n" + comparison.to_string(index=False))
    os.makedirs(RESULTS_DIR, exist_ok=True)
    comparison.to_csv(os.path.join(RESULTS_DIR, 'model_comparison.csv'), index=False)
    print(f"\n  Saved model_comparison.csv")

    # â”€â”€ Forecast visualizations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Forecast Visualizations â”€â”€")
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # -- ARIMA prediction plot
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(test_series.index, test_series.values, color='steelblue',
            linewidth=0.8, label='Actual')
    ax.plot(arima_preds.index, arima_preds.values, color='tomato',
            linewidth=1.2, linestyle='--', label='ARIMA Prediction')
    ax.set_title('ARIMA â€” Actual vs Predicted Traffic', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time'); ax.set_ylabel('Traffic')
    ax.legend(); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(PLOTS_DIR, 'arima_prediction.png'), bbox_inches='tight')
    plt.close(fig)
    print("  Saved arima_prediction.png")

    # -- LSTM prediction plot
    lstm_common = test_series.index.intersection(lstm_preds.index)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(test_series.loc[lstm_common].index, test_series.loc[lstm_common].values,
            color='steelblue', linewidth=0.8, label='Actual')
    ax.plot(lstm_preds.index, lstm_preds.values, color='seagreen',
            linewidth=1.2, linestyle='--', label='LSTM Prediction')
    ax.set_title('LSTM â€” Actual vs Predicted Traffic', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time'); ax.set_ylabel('Traffic')
    ax.legend(); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(PLOTS_DIR, 'lstm_prediction.png'), bbox_inches='tight')
    plt.close(fig)
    print("  Saved lstm_prediction.png")

    # -- Combined comparison plot
    combined_idx = test_series.index.intersection(arima_preds.index).intersection(lstm_preds.index)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(test_series.loc[combined_idx].index, test_series.loc[combined_idx].values,
            color='steelblue', linewidth=0.8, label='Actual', alpha=0.8)
    ax.plot(arima_preds.loc[combined_idx].index, arima_preds.loc[combined_idx].values,
            color='tomato', linewidth=1.1, linestyle='--', label='ARIMA')
    ax.plot(lstm_preds.loc[combined_idx].index, lstm_preds.loc[combined_idx].values,
            color='seagreen', linewidth=1.1, linestyle=':', label='LSTM')
    ax.set_title('Model Comparison â€” Actual vs ARIMA vs LSTM', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time'); ax.set_ylabel('Traffic')
    ax.legend(); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    fig.savefig(os.path.join(PLOTS_DIR, 'model_comparison.png'), bbox_inches='tight')
    plt.close(fig)
    print("  Saved model_comparison.png")

    # â”€â”€ Step 11: Anomaly Detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Step 11: Anomaly Detection â”€â”€")
    best_pred = arima_preds if arima_metrics['RMSE'] <= lstm_metrics['RMSE'] else lstm_preds
    best_label = 'ARIMA' if arima_metrics['RMSE'] <= lstm_metrics['RMSE'] else 'LSTM'
    anomalies_df, anom_stats = detect_anomalies(test_series, best_pred, label=best_label)

    # â”€â”€ Final Report â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ”€â”€ Final Conclusion â”€â”€")
    better_model = 'ARIMA' if arima_metrics['RMSE'] <= lstm_metrics['RMSE'] else 'LSTM'

    report_lines = [
        "=" * 60,
        "  FINAL CONCLUSION â€” Traffic Forecasting Mini-Project",
        "=" * 60,
        "",
        "EDA Findings:",
        f"  - Traffic shows clear daily periodicity.",
        f"  - Peak traffic hour: {eda_findings.get('peak_hour', 'N/A')}:00.",
        f"  - Weekday avg: {eda_findings.get('weekday_avg', 'N/A')}  |  "
        f"Weekend avg: {eda_findings.get('weekend_avg', 'N/A')}.",
        f"  - Traffic variability (CV): {eda_findings.get('cv_pct', 'N/A')}%.",
        "",
        "Feature Engineering:",
        "  - Time features used: hour, day_of_week, is_weekend.",
        "  - Lag features: lag_1, lag_3, lag_6 (5-min steps).",
        "  - Rolling features: rolling_mean (6-step), rolling_std (6-step).",
        "",
        "Forecasting Results:",
        f"  ARIMA  MAE={arima_metrics['MAE']}  RMSE={arima_metrics['RMSE']}  "
        f"(fitted in {round(arima_time,1)}s)",
        f"  LSTM   MAE={lstm_metrics['MAE']}   RMSE={lstm_metrics['RMSE']}  "
        f"(trained in {round(lstm_time,1)}s)",
        f"  â†’ {better_model} performed better on this dataset.",
        "",
        "Anomaly Detection:",
        f"  - Total test observations : {anom_stats['total']}",
        f"  - Unusual observations    : {anom_stats['n_anomalies']}  "
        f"({anom_stats['pct']}%)",
        f"  - Error threshold used    : {anom_stats['threshold']}",
        "",
        "Overall:",
        "  The project demonstrated a complete traffic analysis pipeline:",
        "  dataset ingestion â†’ EDA â†’ feature extraction â†’ ARIMA/LSTM",
        "  forecasting â†’ evaluation â†’ anomaly detection.",
        "  Both classical (ARIMA) and deep-learning (LSTM) approaches were",
        "  compared using MAE and RMSE on a held-out chronological test set.",
        "  Unusual observations were flagged using a 3-sigma error threshold.",
        "=" * 60,
    ]

    report = "\n".join(report_lines)
    print("\n" + report)

    report_path = os.path.join(RESULTS_DIR, 'final_conclusion.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n  Saved final_conclusion.txt")

    print("\nâœ“ Pipeline complete. All outputs saved to outputs/")
    print(f"  Plots  : {PLOTS_DIR}")
    print(f"  Results: {RESULTS_DIR}\n")


if __name__ == '__main__':
    main()

