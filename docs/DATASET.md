# Dataset Guide

Documentation of supported datasets, data formats, and limitations.

---

## 1. Recommended Public Datasets

### 1.1 Retail Sales Dataset

**Description**: Historical retail sales data with product information, sales quantities, and promotional flags.

**Source**: [Kaggle - Retail Sales Dataset](https://www.kaggle.com/datasets/manjeetsingh/retaildataset)

**Features**:
| Column | Type | Description |
|--------|------|-------------|
| Store | int | Store identifier |
| Dept | int | Department identifier |
| Date | date | Week of the sale |
| Weekly_Sales | float | Weekly sales amount |
| IsHoliday | bool | Whether the week contains a holiday |

**Use Case**: Multi-store demand forecasting with holiday effects.

---

### 1.2 Online Retail Dataset (UCI)

**Description**: Transactional data from a UK-based online retail store. Contains all transactions from 2010-2011.

**Source**: [UCI ML Repository - Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/Online+Retail)

**Features**:
| Column | Type | Description |
|--------|------|-------------|
| InvoiceNo | string | Invoice number (C = cancelled) |
| StockCode | string | Product code |
| Description | string | Product description |
| Quantity | int | Number of items purchased |
| InvoiceDate | datetime | Date and time of transaction |
| UnitPrice | float | Price per unit |
| CustomerID | int | Customer identifier |
| Country | string | Customer country |

**Use Case**: Customer-level demand forecasting, product-level sales prediction.

---

### 1.3 Walmart Sales Forecasting

**Description**: Historical sales data for 45 Walmart stores across 99 departments, with holiday and economic indicators.

**Source**: [Kaggle - Walmart Recruiting - Store Sales Forecasting](https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting)

**Features**:
| Column | Type | Description |
|--------|------|-------------|
| Store | int | Store number |
| Dept | int | Department number |
| Date | date | Week date |
| Weekly_Sales | float | Weekly sales amount |
| IsHoliday | bool | Holiday week flag |

**Additional files**:
- `stores.csv`: Store type (A/B/C), size, cluster
- `features.csv`: Temperature, fuel price, CPI, unemployment, markdown events

**Use Case**: Large-scale demand forecasting with external economic factors.

---

### 1.4 Additional Recommended Datasets

| Dataset | Source | Best For |
|---------|--------|----------|
| [Corporacion Favorita](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting) | Kaggle | Grocery demand with promotions |
| [M5 Forecasting](https://www.kaggle.com/competitions/m5-forecasting-accuracy) | Kaggle | Hierarchical retail forecasting |
| [Rossmann Store Sales](https://www.kaggle.com/competitions/rossmann-store-sales) | Kaggle | Store-level daily sales |
| [Bike Sharing Demand](https://www.kaggle.com/competitions/bike-sharing-demand) | Kaggle | Hourly demand with weather |

---

## 2. Data Requirements

### Minimum Data Requirements
| Requirement | Value | Rationale |
|-------------|-------|-----------|
| Minimum rows | 30 | Need at least 30 data points for lag features |
| Recommended rows | 365+ | Full year of data captures yearly seasonality |
| Date range | Continuous | Gaps in dates reduce forecast accuracy |
| Target column | Required | Must have a numeric demand/sales column |

### Required Columns

At minimum, your dataset must contain:

| Column | Type | Description |
|--------|------|-------------|
| date | date/datetime | Transaction date |
| quantity/demand/sales | int/float | Target variable (what to forecast) |

### Optional Columns

| Column | Type | Description | Effect on Features |
|--------|------|-------------|-------------------|
| product_id | int/string | Product identifier | Per-product forecasting |
| category | string | Product category | Category-level patterns |
| promotion | bool/int | Promotion flag | Promotion impact features |
| discount | float | Discount amount | Price sensitivity features |
| holiday | bool | Holiday flag | Holiday demand patterns |
| store_location | string | Store identifier | Location-specific patterns |
| unit_price | float | Price per unit | Price elasticity features |
| temperature | float | Temperature | Weather impact (external) |
| fuel_price | float | Fuel price | Economic indicator |

---

## 3. Target Variable

The system forecasts **demand** or **sales quantity** for a product over future time periods.

### Supported Target Column Names
The system auto-detects the target column by searching for columns containing:
- `demand`
- `sales`
- `quantity`
- `target`

### Target Variable Characteristics
- **Type**: Numeric (integer or float)
- **Minimum value**: 0 (negative demand is clipped to 0)
- **Aggregation**: Daily sums when multiple transactions exist per day
- **Zero handling**: Zero-demand days are included in the training data

---

## 4. Data Limitations

### Known Limitations

| Limitation | Description | Mitigation |
|-----------|-------------|------------|
| **Cold start** | New products with no sales history | Use category-level averages as baseline |
| **Intermittent demand** | Products with many zero-demand days | Prophet handles this better than ML models |
| **External factors** | System does not ingest weather, economic data | Can be added via feature engineering |
| **Multi-location** | Single location supported per model | Product-location combinations need separate models |
| **Seasonality** | Minimum 1 year of data for yearly seasonality | Prophet can estimate with less data but lower accuracy |
| **Promotions** | Historical promotion data needed for accurate forecasting | Binary promotion flag required |
| **Cancellations** | Returned/cancelled sales should be excluded | Filter before uploading |
| **Outliers** | Extreme values (e.g., Black Friday) can skew models | IQR-based clipping applied automatically |

### Data Quality Checks

The `DataCleaner` automatically handles:
- Missing values (median/mode imputation)
- Duplicate rows
- Invalid dates
- Outliers (IQR clipping at 1.5x)

### Recommended Data Quality Steps

Before uploading, consider:
1. **Remove cancelled transactions** - Negative quantities should be excluded
2. **Aggregate to daily level** - Sum transactions per day per product
3. **Remove anomalies** - One-time events (e.g., office moves) should be removed
4. **Verify date continuity** - Fill missing dates with zero demand

---

## 5. Custom CSV Upload Format

### Sales Upload CSV

Upload via `POST /api/sales/upload-csv`.

**Required Columns:**
```csv
product_id,quantity,unit_price
```

**Full Format (with optional columns):**
```csv
product_id,quantity,unit_price,discount,notes,sale_date
1,5,29.99,0.0,Regular sale,2024-01-15
2,3,49.99,5.0,Bulk order,2024-01-15
1,2,29.99,0.0,,2024-01-16
3,10,9.99,0.0,Promotional,2024-01-16
```

**Column Descriptions:**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| product_id | int | Yes | Must match existing product ID |
| quantity | int | Yes | Number of units sold (must be > 0) |
| unit_price | float | Yes | Selling price per unit |
| discount | float | No | Discount applied (default: 0) |
| notes | string | No | Optional sale notes |
| sale_date | date | No | Sale date YYYY-MM-DD (default: today) |

### ML Training CSV

For direct ML training via the forecast endpoints:

**Full Format:**
```csv
date,product_id,demand,price,promotion,category,holiday
2024-01-01,1,45,29.99,0,Electronics,1
2024-01-02,1,52,29.99,0,Electronics,0
2024-01-03,1,38,24.99,1,Electronics,0
2024-01-04,1,61,29.99,0,Electronics,0
```

**Column Descriptions:**
| Column | Type | Description |
|--------|------|-------------|
| date | date | Transaction date (YYYY-MM-DD) |
| product_id | int | Product identifier |
| demand/sales/quantity | int | Target variable |
| price | float | Unit price |
| promotion | bool/int | Promotion active (0/1) |
| category | string | Product category |
| holiday | bool/int | Holiday flag (0/1) |

---

## 6. Dataset Preparation Guide

### Step 1: Aggregate to Daily Level
```python
import pandas as pd

df = pd.read_csv('raw_sales.csv')
df['date'] = pd.to_datetime(df['date'])

# Aggregate to daily level per product
daily = df.groupby(['date', 'product_id']).agg({
    'quantity': 'sum',
    'unit_price': 'mean',
    'promotion': 'max'
}).reset_index()
```

### Step 2: Fill Missing Dates
```python
# Create complete date range
date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')

# Reindex and fill missing with 0
daily = daily.set_index('date').reindex(date_range, fill_value=0)
```

### Step 3: Handle Outliers
```python
# Cap extreme values
Q1 = df['quantity'].quantile(0.25)
Q3 = df['quantity'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
df['quantity'] = df['quantity'].clip(lower, upper)
```

### Step 4: Save Cleaned Data
```python
daily.to_csv('data/processed/clean_sales.csv', index=False)
```

---

## 7. Dataset Size Guidelines

| Dataset Size | Recommended Models | Training Time |
|-------------|-------------------|---------------|
| < 100 rows | Linear Regression, Prophet | Seconds |
| 100-500 rows | + Random Forest | Seconds |
| 500-2000 rows | + XGBoost, LightGBM | Seconds to minutes |
| 2000-10000 rows | All models | Minutes |
| 10000+ rows | All models (may need LSTM optimization) | Minutes to hours |

### Memory Considerations
- Feature engineering can expand dataset width significantly
- Lag features (lag_1 through lag_30) add 30+ columns
- Rolling features add 6+ columns
- LSTM sequences require 30x reshaping
- Recommended: At least 4GB RAM for datasets with 10K+ rows
