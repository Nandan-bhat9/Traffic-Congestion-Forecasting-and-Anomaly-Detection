# Traffic Congestion Forecasting and Anomaly Detection

> An end-to-end Machine Learning and Deep Learning system for urban traffic time-series forecasting and anomaly detection, comparing classical statistical methods (**ARIMA**) against recurrent neural networks (**LSTM**).

---

## 📌 Project Overview

Urban traffic congestion presents serious economic, environmental, and infrastructural challenges. This project provides a full data science pipeline that analyzes historical traffic sensor data to:
1. **Forecast Traffic Congestion**: Evaluates and compares **ARIMA** (Autoregressive Integrated Moving Average) and **LSTM** (Long Short-Term Memory) deep neural networks.
2. **Detect Anomalies**: Identifies unusual traffic events and disruptions using forecast error distributions and statistical thresholding.
3. **Comprehensive Reporting**: Generates automated visual plots, performance metrics, and a full academic LaTeX report.

---

## 🏗️ Repository Structure

```
ADS/
├── traffic-forecasting/               # Core pipeline package
│   ├── data/
│   │   ├── raw/                      # Raw sensor time-series data
│   │   └── processed/                # Preprocessed & scaled data
│   ├── models/                       # Saved trained models (.keras)
│   ├── outputs/
│   │   ├── plots/                    # Generated EDA, forecasts, & anomaly plots
│   │   └── results/                  # Model metrics & anomaly reports (.csv, .txt)
│   ├── report/                       # LaTeX report sources & compiled PDF
│   ├── src/
│   │   ├── data_loader.py            # Dataset synthesis and ingestion
│   │   ├── preprocessing.py         # Data cleaning, interpolation, scaling
│   │   ├── eda.py                   # Exploratory data analysis & visualizations
│   │   ├── features.py              # Temporal feature engineering & lags
│   │   ├── arima_model.py           # Statistical ARIMA training & inference
│   │   ├── lstm_model.py            # Deep LSTM neural network architecture
│   │   ├── anomaly_detection.py     # Residual-based anomaly detection
│   │   └── evaluation.py            # MAE, RMSE metrics calculation
│   ├── main.py                       # Unified pipeline execution entrypoint
│   ├── requirements.txt              # Python package dependencies
│   └── README.md                     # Pipeline-specific documentation
├── latex_report/                     # LaTeX report sources and assets
├── Traffic_Forecasting_Report.pdf    # Compiled comprehensive project report
├── prd.md                            # Product Requirements Document
└── .gitignore                        # Git ignore specifications
```

---

## ⚙️ Methodology & Pipeline

```
Raw Traffic Data (CSV)
         │
         ▼
Data Cleaning & Imputation (src/preprocessing.py)
         │
         ▼
Exploratory Data Analysis (src/eda.py)
         │
         ▼
Feature Engineering & Windowing (src/features.py)
         │
    ┌────┴────────────────────────┐
    ▼                             ▼
ARIMA Model                   LSTM Model
(src/arima_model.py)          (src/lstm_model.py)
    │                             │
    └────┬────────────────────────┘
         ▼
Model Evaluation (MAE, RMSE) (src/evaluation.py)
         │
         ▼
Anomaly Detection via Residuals (src/anomaly_detection.py)
         │
         ▼
Visualizations & Reports (outputs/ & report/)
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9 or higher

### 2. Installation
Navigate into the `traffic-forecasting` directory and install the required dependencies:
```bash
cd traffic-forecasting
pip install -r requirements.txt
```

### 3. Run the Complete Pipeline
Run `main.py` to execute the full pipeline (data generation/loading, preprocessing, EDA, model training, evaluation, and anomaly detection):
```bash
python main.py
```

### 4. Pipeline Outputs
All outputs are saved automatically:
- **Plots**: `traffic-forecasting/outputs/plots/`
  - `traffic_over_time.png` — Global time series trend
  - `hourly_traffic.png` & `daily_traffic.png` — Diurnal and weekly periodicity
  - `arima_prediction.png` & `lstm_prediction.png` — Model predictions vs ground truth
  - `model_comparison.png` — Side-by-side forecast comparison
  - `anomalies.png` — Flagged traffic anomalies
- **Metrics**: `traffic-forecasting/outputs/results/model_comparison.csv`
- **Detected Anomalies**: `traffic-forecasting/outputs/results/anomalies.csv`

---

## 📊 Models & Comparative Performance

| Model | Type | Strengths |
|---|---|---|
| **ARIMA** | Classical Time Series | Interpretable, fast training, strong on stationary linear trends |
| **LSTM** | Deep Recurrent Network | Captures complex non-linear dynamics, long-term temporal dependencies |

Evaluation metrics computed: **MAE** (Mean Absolute Error) and **RMSE** (Root Mean Squared Error).

---

## 📄 Documentation & Reports
- **Complete Project Report**: Refer to [Traffic_Forecasting_Report.pdf](Traffic_Forecasting_Report.pdf) for the complete IEEE/academic report.
- **LaTeX Source Code**: Available in `latex_report/` and `traffic-forecasting/report/`.
- **System Requirements**: Detailed in [prd.md](prd.md).
