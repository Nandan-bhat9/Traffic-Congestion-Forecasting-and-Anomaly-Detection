# PRD: Traffic Congestion Forecasting and Anomaly Detection

## 1. Project Overview

Build a small machine-learning project that uses publicly available traffic sensor data to analyze traffic patterns, forecast future traffic congestion, and detect unusual traffic behavior.

The project will be developed and executed using **Antigravity** as the development environment.

This is a **college mini-project**, so the implementation must remain simple, lightweight, and easy to explain.

The project should compare:

* **ARIMA** — classical time-series forecasting
* **LSTM** — deep-learning time-series forecasting

The project should also perform basic anomaly detection using forecasting errors.

---

# 2. Main Objectives

The system should:

1. Download a publicly available traffic sensor dataset.
2. Clean and prepare the data.
3. Perform Exploratory Data Analysis (EDA).
4. Identify traffic patterns from the EDA.
5. Extract useful time-series features.
6. Train a simple ARIMA model.
7. Train a small LSTM model.
8. Compare their forecasting performance.
9. Detect unusual traffic observations.
10. Visualize the results.
11. Generate final conclusions.

---

# 3. Scope

### Included

* Public traffic dataset
* Data preprocessing
* EDA
* Time-series feature extraction
* ARIMA
* LSTM
* Forecasting
* Anomaly detection
* Model comparison
* Visualizations
* Results and conclusions

### Not Included

Do NOT implement:

* Real-time traffic monitoring
* CCTV
* Traffic cameras
* IoT devices
* Live APIs
* Web applications
* Dashboards
* Transformers
* GRU
* CNN-LSTM
* Complex ensemble models
* Hyperparameter optimization
* Deployment
* Docker
* Cloud infrastructure

Keep the project focused on **offline traffic time-series analysis**.

---

# 4. Dataset

Use a publicly available traffic sensor dataset.

### Preferred dataset

**METR-LA**

METR-LA contains traffic measurements collected from multiple traffic sensors.

If using METR-LA requires excessive preprocessing or causes compatibility problems, use another publicly available traffic sensor dataset containing:

```text
timestamp
traffic measurement
sensor ID/location
```

The dataset source must be documented in the project README.

---

# 5. Dataset Simplification

Traffic datasets can contain many sensors.

For this mini-project:

**Do not train models on all sensors.**

Select **one representative sensor** with sufficient continuous data.

The workflow should become:

```text
Large Traffic Dataset
        ↓
Select One Sensor
        ↓
Single Traffic Time Series
        ↓
EDA
        ↓
Feature Extraction
        ↓
ARIMA + LSTM
```

If necessary, use a limited time period or reasonable subset of the selected sensor's data to keep training fast.

---

# 6. Technology Stack

Use Python.

Required libraries:

```text
pandas
numpy
matplotlib
seaborn
scikit-learn
statsmodels
tensorflow / keras
```

Optional:

```text
requests
```

for downloading the dataset if required.

Do not introduce unnecessary frameworks.

---

# 7. Project Structure

Create a clean but simple project structure:

```text
traffic-forecasting/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│
├── outputs/
│   ├── plots/
│   └── results/
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── eda.py
│   ├── features.py
│   ├── arima_model.py
│   ├── lstm_model.py
│   ├── anomaly_detection.py
│   └── evaluation.py
│
├── main.py
├── requirements.txt
└── README.md
```

Do not over-engineer the architecture.

---

# 8. Step 1 — Dataset Download

Create functionality to download the selected public dataset.

The downloaded data should be stored inside:

```text
data/raw/
```

The application should check whether the dataset already exists before downloading it again.

Example workflow:

```text
Check dataset
     ↓
Exists?
 ┌───┴───┐
Yes     No
 ↓       ↓
Load   Download
```

---

# 9. Step 2 — Data Preprocessing

Perform basic preprocessing.

Tasks:

* Load dataset.
* Inspect columns.
* Convert timestamps to datetime.
* Sort chronologically.
* Check missing values.
* Handle missing traffic values.
* Remove duplicates if required.
* Select one sensor.
* Rename the traffic column to `traffic`.
* Set timestamp as the index.

For missing values, use simple interpolation where appropriate.

Do not implement complicated missing-data algorithms.

---

# 10. Step 3 — Exploratory Data Analysis

Generate clear graphs using Matplotlib/Seaborn.

### Graph 1 — Traffic over time

Plot:

```text
X-axis → Time
Y-axis → Traffic
```

Purpose:

Understand the overall traffic pattern.

---

### Graph 2 — Traffic distribution

Create a histogram.

Purpose:

Understand the distribution of traffic values.

---

### Graph 3 — Average traffic by hour

Extract:

```python
hour
```

Calculate average traffic for each hour.

Create a graph showing the hourly pattern.

Purpose:

Identify possible peak traffic periods.

---

### Graph 4 — Average traffic by day

Extract:

```python
day_of_week
```

Compare traffic across the days of the week.

---

### Graph 5 — Rolling average

Calculate a rolling mean.

For example:

```text
rolling window = 6
```

Plot:

```text
Actual traffic
Rolling average
```

This should help show the underlying trend.

---

### Graph 6 — Correlation heatmap

If the dataset contains multiple useful numerical features, generate a correlation heatmap.

If not useful, skip it.

Do not create meaningless visualizations.

---

# 11. Step 4 — EDA Conclusions

After generating the graphs, produce a short textual summary.

The conclusions must be **calculated from the actual dataset**.

Examples of possible findings:

* Traffic varies significantly throughout the day.
* Certain hours have higher average traffic.
* Weekday and weekend traffic have different patterns.
* Traffic contains short-term fluctuations.
* Rolling averages reveal broader trends.
* Some observations contain unusually large deviations.

Do not hard-code conclusions without checking the actual data.

Save the findings to:

```text
outputs/results/eda_findings.txt
```

---

# 12. Step 5 — Feature Extraction

Create simple time-series features.

### Time features

```text
hour
day_of_week
is_weekend
```

### Lag features

Create a small number of lag values:

```text
lag_1
lag_2
lag_3
```

If the dataset's sampling frequency makes more sense, use:

```text
lag_1
lag_3
lag_6
```

### Rolling features

Create:

```text
rolling_mean
rolling_std
```

These represent recent traffic behavior.

---

# 13. Step 6 — Train/Test Split

Use a chronological split.

**Never randomly shuffle the time-series data.**

Use:

```text
80% → Training
20% → Testing
```

Example:

```text
Earlier observations
        ↓
     TRAINING
        ↓
-------------------
        ↓
      TESTING
        ↓
Later observations
```

This prevents future information from leaking into training.

---

# 14. Step 7 — ARIMA Model

Implement a simple ARIMA model using `statsmodels`.

Example:

```python
ARIMA(train_data, order=(2,1,2))
```

The exact parameters may be adjusted if necessary.

Do not perform expensive grid searches.

### ARIMA workflow

```text
Training data
     ↓
ARIMA
     ↓
Forecast
     ↓
Compare with actual test data
```

Calculate:

* MAE
* RMSE

Save the prediction results.

---

# 15. Step 8 — LSTM Model

Implement a small LSTM model using TensorFlow/Keras.

Create sequences from historical traffic observations.

Example:

```text
12 previous observations
          ↓
       LSTM(32)
          ↓
      Dropout
          ↓
       Dense
          ↓
Next traffic value
```

Suggested architecture:

```python
Sequential([
    LSTM(32, input_shape=(sequence_length, 1)),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1)
])
```

Keep it small.

---

# 16. LSTM Training

Do not train for a long time.

Recommended:

```text
epochs: 10–20
batch_size: 32
```

Use EarlyStopping.

Example:

```python
EarlyStopping(
    monitor="loss",
    patience=3,
    restore_best_weights=True
)
```

The goal is to demonstrate LSTM forecasting, not perform extensive optimization.

---

# 17. Step 9 — Model Evaluation

Evaluate both models using:

### MAE

Mean Absolute Error.

### RMSE

Root Mean Squared Error.

Optional:

### MAPE

Use MAPE only if the target values do not contain zeros or values close to zero.

---

# 18. Step 10 — Model Comparison

Generate a results table automatically.

Example:

```text
Model     MAE     RMSE
------------------------
ARIMA     X.XX    X.XX
LSTM      X.XX    X.XX
```

Do not manually enter these values.

Calculate them from the actual predictions.

Also record approximate training time.

Example:

```text
Model     MAE     RMSE     Training Time
-----------------------------------------
ARIMA     ...     ...      ...
LSTM      ...     ...      ...
```

---

# 19. Forecast Visualization

Create separate graphs for:

### ARIMA

```text
Actual Traffic
vs
ARIMA Prediction
```

### LSTM

```text
Actual Traffic
vs
LSTM Prediction
```

Also create one comparison graph:

```text
Actual
ARIMA
LSTM
```

Use the same test period for all models.

---

# 20. Step 11 — Anomaly Detection

Use a simple forecasting-error-based approach.

Calculate:

```python
error = abs(actual - predicted)
```

Use a statistical threshold:

```python
threshold = error.mean() + 3 * error.std()
```

Mark:

```text
error > threshold
```

as an anomaly.

This should identify observations where actual traffic differs substantially from the expected traffic.

---

# 21. Anomaly Visualization

Create a graph:

```text
Actual traffic
     +
     |
     |        ●
     |   /\  / \
     |__/  \/   \____
     |
     +------------------→ Time
          anomaly
```

Anomalies should be clearly highlighted.

The graph should include:

* Traffic line
* Anomaly points
* Time axis
* Traffic axis
* Legend

---

# 22. Anomaly Results

Automatically calculate:

```text
Total test observations
Number of anomalies
Anomaly percentage
```

Also produce a small table:

```text
Timestamp | Traffic | Prediction | Error
```

for detected anomalies.

Do not claim that an anomaly represents an accident, road closure, or specific real-world event unless the dataset contains information verifying that event.

Call them:

**"unusual traffic observations"**

---

# 23. Final Results

Create:

```text
outputs/results/model_comparison.csv
outputs/results/anomalies.csv
outputs/results/eda_findings.txt
```

Save graphs to:

```text
outputs/plots/
```

Suggested filenames:

```text
traffic_over_time.png
traffic_distribution.png
hourly_traffic.png
daily_traffic.png
rolling_average.png
arima_prediction.png
lstm_prediction.png
model_comparison.png
anomalies.png
```

---

# 24. Final Conclusion

Generate a concise final report containing:

### EDA Findings

What patterns were observed?

### Feature Findings

Which temporal/lag features were used?

### Forecasting Findings

How did ARIMA perform?

How did LSTM perform?

### Anomaly Findings

How many unusual observations were detected?

### Overall Conclusion

Explain what the experiment demonstrates.

The conclusion must be based on the actual calculated results.

Example format:

```text
The traffic data showed clear temporal variation across the observation
period. Time-based and lag-based features were used to represent traffic
behavior.

ARIMA provided a classical time-series baseline, while LSTM was used to
model sequential patterns using previous observations.

Both models were evaluated using MAE and RMSE on a chronological test set.
The model with the lower error on this dataset provided more accurate
forecasts for this experiment.

Forecasting errors were also used to identify unusual traffic
observations. These anomalies represent traffic behavior that deviated
substantially from the model's expected values.
```

---

# 25. README

Create a `README.md` containing:

## Project Title

Traffic Congestion Forecasting and Anomaly Detection

## Problem Statement

Brief explanation of the problem.

## Objectives

List the project objectives.

## Dataset

Mention:

* Dataset name
* Source
* Description

## Technologies

```text
Python
Pandas
NumPy
Matplotlib
Seaborn
Scikit-learn
Statsmodels
TensorFlow/Keras
```

## Methodology

```text
Dataset
 ↓
Preprocessing
 ↓
EDA
 ↓
Feature Extraction
 ↓
ARIMA + LSTM
 ↓
Evaluation
 ↓
Anomaly Detection
 ↓
Results
```

## Results

Automatically update this section with the final model metrics if practical.

## How to Run

Provide simple instructions for running the project in Antigravity.

---

# 26. Important Constraints for Antigravity

The implementation must remain a **mini-project**.

### Do:

* Keep code readable.
* Keep models small.
* Use one sensor.
* Use a manageable amount of data.
* Train quickly.
* Generate useful graphs.
* Automatically calculate metrics.
* Save outputs.
* Explain each major step.

### Do not:

* Build a complicated software architecture.
* Create a web application.
* Add unnecessary APIs.
* Train large neural networks.
* Use multiple deep-learning architectures.
* Perform extensive hyperparameter tuning.
* Use unnecessarily large datasets.
* Add features that are unrelated to the project objective.

---

# 27. Expected Final Output

The completed Antigravity project should contain:

```text
traffic-forecasting/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│
├── outputs/
│   ├── plots/
│   └── results/
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── eda.py
│   ├── features.py
│   ├── arima_model.py
│   ├── lstm_model.py
│   ├── anomaly_detection.py
│   └── evaluation.py
│
├── main.py
├── requirements.txt
└── README.md
```

The complete workflow should be executable from `main.py`.

The final project should produce the dataset, processed data, graphs, model predictions, evaluation metrics, anomaly results, and conclusions automatically.

## Core Principle

**Keep the project simple enough for a mini-project, but complete enough to demonstrate the entire machine-learning pipeline:**

**Data → EDA → Feature Extraction → Forecasting → Model Comparison → Anomaly Detection → Conclusions**
