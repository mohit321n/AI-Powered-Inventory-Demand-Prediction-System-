# ML Methodology

Detailed documentation of the machine learning pipeline, feature engineering, model selection, and evaluation approach.

---

## 1. Data Preprocessing

The `DataCleaner` class (`backend/ml/preprocessing/data_cleaner.py`) handles all data cleaning steps:

### Step 1: Data Loading
- Load CSV files using pandas
- Automatic detection of date columns by name pattern matching

### Step 2: Missing Value Handling
- **Threshold-based column dropping**: Columns with >50% missing values are dropped entirely
- **Numerical columns**: Filled with median value (robust to outliers)
- **Categorical columns**: Filled with mode (most frequent value)
- **Fallback**: If no mode exists, rows are dropped

### Step 3: Duplicate Removal
- Exact duplicate rows are removed to prevent data leakage in training

### Step 4: Date Validation
- Automatic detection of date columns (looks for columns containing "date" in the name)
- Conversion to datetime using `pd.to_datetime` with `infer_datetime_format`
- Invalid dates (NaT) are dropped
- Data is sorted chronologically for time-series operations

### Step 5: Outlier Detection & Treatment
- **Method**: Interquartile Range (IQR) method
- **Factor**: 1.5x IQR (standard Tukey fences)
- **Treatment**: Outliers are clipped to the fence boundaries (not removed)
- **Columns**: Applied to all numerical columns by default

---

## 2. Feature Engineering

The `FeatureBuilder` class (`backend/ml/feature_engineering/feature_builder.py`) creates features from raw data:

### 2.1 Time Features

| Feature | Description | Why It's Used |
|---------|-------------|---------------|
| `day` | Day of month (1-31) | Captures intra-month patterns (e.g., payday effects) |
| `week` | ISO week number (1-52) | Captures weekly patterns across the year |
| `month` | Month number (1-12) | Captures monthly/seasonal patterns |
| `quarter` | Quarter (1-4) | Captures quarterly business cycles |
| `year` | Year | Handles multi-year trends |
| `day_of_week` | Day index (0=Monday, 6=Sunday) | Captures weekly demand patterns |
| `is_weekend` | Binary (0/1) | Weekend vs weekday demand differences |

### 2.2 Lag Features

| Feature | Description | Why It's Used |
|---------|-------------|---------------|
| `lag_1` | Previous day's demand | Captures immediate autocorrelation |
| `lag_7` | Demand 7 days ago | Captures weekly seasonality |
| `lag_14` | Demand 14 days ago | Captures bi-weekly patterns |
| `lag_30` | Demand 30 days ago | Captures monthly seasonality |

### 2.3 Rolling Features

| Feature | Description | Why It's Used |
|---------|-------------|---------------|
| `rolling_mean_7` | 7-day moving average | Smooths short-term noise, captures weekly trend |
| `rolling_std_7` | 7-day rolling std | Measures recent demand volatility |
| `rolling_mean_14` | 14-day moving average | Captures bi-weekly trend |
| `rolling_std_14` | 14-day rolling std | Measures medium-term volatility |
| `rolling_mean_30` | 30-day moving average | Captures monthly trend |
| `rolling_std_30` | 30-day rolling std | Measures long-term volatility |

### 2.4 Calendar Features

| Feature | Description | Why It's Used |
|---------|-------------|---------------|
| `is_holiday` | US federal holiday flag | Holidays significantly impact demand |
| `is_month_start` | First day of month | Beginning-of-month purchasing patterns |
| `is_month_end` | Last day of month | End-of-month purchasing patterns |
| `is_quarter_start` | First day of quarter | Quarterly business cycle effects |
| `is_quarter_end` | Last day of quarter | Quarterly close effects |
| `is_year_start` | First day of year | New year effects |
| `is_year_end` | Last day of year | Year-end effects |
| `is_promotion` | Promotion active flag | Promotions drive demand spikes |

### 2.5 Demand Features

| Feature | Description | Why It's Used |
|---------|-------------|---------------|
| `prev_month_demand` | Demand 30 days ago | Month-over-month comparison |
| `prev_year_demand` | Demand 365 days ago | Year-over-year comparison |
| `prev_month_avg` | 30-day rolling average (shifted) | Recent baseline demand level |
| `prev_year_avg` | 365-day rolling average (shifted) | Long-term baseline demand level |

---

## 3. Model Selection Rationale

### Linear Regression
- **Type**: Linear baseline model
- **Use**: Establishes a performance floor; simple, interpretable, fast
- **Strengths**: No hyperparameter tuning, interpretable coefficients, fast training
- **Weaknesses**: Cannot capture non-linear relationships

### Random Forest
- **Type**: Bagging ensemble
- **Use**: Captures non-linear feature interactions without explicit feature engineering
- **Strengths**: Robust to outliers, handles mixed feature types, feature importance
- **Weaknesses**: Can overfit on small datasets, slower prediction than linear models
- **Hyperparameters**: `n_estimators=100`, `random_state=42`, `n_jobs=-1`

### XGBoost
- **Type**: Gradient boosting ensemble
- **Use**: State-of-the-art for tabular data; often best performer
- **Strengths**: High accuracy, handles missing values, regularization, feature importance
- **Weaknesses**: Slower training, more prone to overfitting without tuning
- **Hyperparameters**: `n_estimators=100`, `learning_rate=0.1`, `random_state=42`

### LightGBM
- **Type**: Gradient boosting ensemble (leaf-wise)
- **Use**: Fast training on large datasets with comparable accuracy to XGBoost
- **Strengths**: Fastest training, low memory usage, native categorical support
- **Weaknesses**: Can overfit on small datasets
- **Hyperparameters**: `n_estimators=100`, `learning_rate=0.1`, `random_state=42`

### LSTM (Long Short-Term Memory)
- **Type**: Recurrent neural network
- **Use**: Captures complex temporal dependencies and long-range patterns
- **Strengths**: Learns sequential patterns automatically, handles variable-length sequences
- **Weaknesses**: Requires more data, slower training, less interpretable, requires GPU for large datasets
- **Architecture**: 64-unit LSTM -> Dropout(0.2) -> 32-unit LSTM -> Dropout(0.2) -> Dense(16, relu) -> Dense(1)
- **Input**: 30-day lookback sequences, scaled with MinMaxScaler

### Facebook Prophet
- **Type**: Additive time-series model
- **Use**: Built for business time-series with strong seasonal effects
- **Strengths**: Handles holidays, multiple seasonalities, trend changepoints out of the box
- **Weaknesses**: Less flexible for complex patterns, slower than tree models
- **Parameters**: `yearly_seasonality=True`, `weekly_seasonality=True`, `changepoint_prior_scale=0.05`

---

## 4. Training Pipeline

```
Raw CSV Data
     |
     v
[Data Cleaning] ---- Missing values, duplicates, outliers, date validation
     |
     v
[Feature Engineering] ---- Time, lag, rolling, calendar, demand features
     |
     v
[Train/Validation Split] ---- Time-based split (80/20)
     |
     v
[Model Training] ---- Train all 6 models on training set
     |
     v
[Evaluation] ---- Evaluate all models on validation set
     |
     v
[Model Comparison] ---- Compare MAE, RMSE, MAPE, R-squared
     |
     v
[Best Model Selection] ---- Select model with lowest RMSE
     |
     v
[Save Model] ---- Persist to disk with pickle/joblib
```

### Data Split Strategy
- **Time-based split**: First 80% for training, last 20% for validation
- **No random shuffling**: Preserves temporal order to prevent data leakage
- **Rationale**: Time-series data must not use future data for training

---

## 5. Evaluation Metrics

### MAE (Mean Absolute Error)
```
MAE = (1/n) * Σ|y_true - y_pred|
```
- **Interpretation**: Average magnitude of prediction errors in the same units as the target
- **Range**: [0, +∞), lower is better
- **Use**: Easy to explain to stakeholders

### RMSE (Root Mean Squared Error)
```
RMSE = √[(1/n) * Σ(y_true - y_pred)²]
```
- **Interpretation**: Penalizes large errors more than MAE
- **Range**: [0, +∞), lower is better
- **Use**: Primary metric for model selection (used to choose best model)

### MAPE (Mean Absolute Percentage Error)
```
MAPE = (100/n) * Σ|y_true - y_pred| / |y_true|
```
- **Interpretation**: Percentage error, scale-independent
- **Range**: [0, 100%], lower is better
- **Use**: Comparing forecast accuracy across products with different demand levels
- **Note**: Undefined when y_true = 0; handled by filtering zero values

### R-squared (Coefficient of Determination)
```
R² = 1 - (SS_res / SS_tot)
```
- **Interpretation**: Proportion of variance in the target explained by the model
- **Range**: (-∞, 1], higher is better; 1.0 = perfect prediction
- **Use**: Measures overall model fit quality

---

## 6. Model Comparison Table

| Model | MAE | RMSE | MAPE (%) | R² | Training Time |
|-------|-----|------|----------|-----|---------------|
| Linear Regression | - | - | - | - | Fast |
| Random Forest | - | - | - | - | Medium |
| XGBoost | - | - | - | - | Medium |
| LightGBM | - | - | - | - | Fast |
| LSTM | - | - | - | - | Slow |
| Prophet | - | - | - | - | Slow |

> Values are populated after training on a specific dataset.

---

## 7. Best Model Selection Logic

```python
def select_best_model(comparison: Dict[str, Dict[str, float]]) -> str:
    # Model with lowest RMSE is selected as best
    best_model = min(comparison, key=lambda m: comparison[m]["rmse"])
    return best_model
```

**Selection Criteria:**
1. **Primary metric**: RMSE (root mean squared error)
2. **Tiebreaker**: R-squared (higher is better)
3. **Fallback**: If all models fail, defaults to Linear Regression

**Why RMSE as primary metric?**
- Penalizes large forecast errors more heavily
- Same units as the target variable (easy to interpret)
- Standard metric in demand forecasting literature

---

## 8. Forecasting Approach

### Direct Multi-Step Forecasting
- Model predicts each future time step independently
- Features are computed from historical data up to the prediction point
- For multi-period forecasts, the model uses the most recent known values

### LSTM Multi-Step Strategy
For LSTM, a recursive forecasting approach is used:
1. Use the last 30 known values as input sequence
2. Predict next value
3. Append prediction to sequence, remove oldest value
4. Repeat for each future period

### Confidence Intervals

The system provides 95% confidence intervals for all forecasts:

**For tree-based models (Random Forest, XGBoost, LightGBM):**
- Uses the variance across individual tree predictions
- Each tree provides an independent estimate
- Standard deviation across all tree predictions forms the interval

**For LSTM:**
- Uses empirical standard deviation of predictions
- Multiplied by a scaling factor (0.5) to account for recursive prediction uncertainty

**For linear models:**
- Uses a fixed proportion of the prediction (10% of predicted value)
- Based on typical residual standard deviation

**Confidence Interval Formula:**
```
lower_bound = prediction - z_score * std
upper_bound = prediction + z_score * std
```
Where z_score = 1.96 for 95% confidence (from scipy.stats.norm.ppf).

Bounds are clipped at 0 (no negative demand predictions).

---

## 9. What-If Analysis

The what-if system allows users to simulate the impact of changes on demand:

### Parameters
| Parameter | Description | Effect |
|-----------|-------------|--------|
| `price_change_pct` | Percentage change in price | Negative % typically increases demand |
| `seasonality_factor` | Multiplier for seasonal patterns | >1 amplifies seasonal peaks |
| `trend_factor` | Multiplier for trend component | >1 increases overall trend |

### Implementation
1. Generate baseline forecast using the trained model
2. Apply adjustment factors to the forecast
3. Present both baseline and adjusted forecasts for comparison

---

## 10. Model Persistence

- Trained models are saved using `pickle` (standard) or `joblib` (for large models)
- Model artifacts stored in `backend/models/` directory
- Model metadata stored in `model_results` database table including:
  - Model name and parameters
  - Evaluation metrics (MAE, RMSE, MAPE, R²)
  - Training timestamp
  - File path to saved model
