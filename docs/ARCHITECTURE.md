# Architecture

System architecture, component descriptions, data flow, and database schema.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  React Frontend (3000)                    │   │
│  │                                                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │Dashboard │ │ Products │ │  Sales   │ │  Forecast  │  │   │
│  │  │  Page    │ │  Page    │ │  Page    │ │  Page      │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │Inventory │ │  Alerts  │ │ What-If  │ │   Login    │  │   │
│  │  │  Page    │ │  Page    │ │  Page    │ │   Page     │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │          Axios HTTP Client + Interceptors           │  │   │
│  │  │  (JWT token injection, 401 redirect handling)       │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                         HTTP/REST                                │
│                              │                                   │
├──────────────────────────────┼───────────────────────────────────┤
│                        API LAYER                                 │
│                              │                                   │
│  ┌───────────────────────────┼──────────────────────────────┐   │
│  │              FastAPI Backend (8000)                       │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │                  API Routers                        │  │   │
│  │  │                                                     │  │   │
│  │  │  /api/auth  /api/products  /api/inventory          │  │   │
│  │  │  /api/sales  /api/forecast  /api/alerts            │  │   │
│  │  │  /api/dashboard                                    │  │   │
│  │  └─────────────────────┬──────────────────────────────┘  │   │
│  │                        │                                  │   │
│  │  ┌─────────────────────┼──────────────────────────────┐  │   │
│  │  │              Middleware Stack                        │  │   │
│  │  │  • CORS Middleware                                   │  │   │
│  │  │  • JWT Authentication                               │  │   │
│  │  │  • Request Validation (Pydantic)                    │  │   │
│  │  │  • Global Exception Handler                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
├──────────────────────────────┼───────────────────────────────────┤
│                      SERVICE LAYER                               │
│                              │                                   │
│  ┌───────────────────────────┼──────────────────────────────┐   │
│  │              Business Logic Services                      │   │
│  │                                                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │  Auth    │ │ Product  │ │Inventory │ │   Sales    │  │   │
│  │  │ Service  │ │ Service  │ │ Service  │ │  Service   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │   │
│  │  │Forecast  │ │  Alert   │ │Dashboard │                 │   │
│  │  │ Service  │ │ Service  │ │ Service  │                 │   │
│  │  └──────────┘ └──────────┘ └──────────┘                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
├──────────────────────────────┼───────────────────────────────────┤
│                      ML PIPELINE LAYER                           │
│                              │                                   │
│  ┌───────────────────────────┼──────────────────────────────┐   │
│  │                                                           │   │
│  │  ┌─────────────┐    ┌─────────────────┐                  │   │
│  │  │   Data       │    │    Feature       │                  │   │
│  │  │   Cleaner    │───▶│    Engineering   │                  │   │
│  │  │              │    │                  │                  │   │
│  │  │ • Missing    │    │ • Time features  │                  │   │
│  │  │   values     │    │ • Lag features   │                  │   │
│  │  │ • Duplicates │    │ • Rolling stats  │                  │   │
│  │  │ • Outliers   │    │ • Calendar       │                  │   │
│  │  │ • Dates      │    │ • Demand features│                  │   │
│  │  └─────────────┘    └────────┬────────┘                  │   │
│  │                              │                            │   │
│  │                    ┌─────────▼─────────┐                  │   │
│  │                    │   Model Trainer    │                  │   │
│  │                    │                    │                  │   │
│  │                    │ ┌────────────────┐ │                  │   │
│  │                    │ │Linear Regression│ │                  │   │
│  │                    │ │Random Forest   │ │                  │   │
│  │                    │ │XGBoost         │ │                  │   │
│  │                    │ │LightGBM        │ │                  │   │
│  │                    │ │LSTM            │ │                  │   │
│  │                    │ │Prophet         │ │                  │   │
│  │                    │ └────────────────┘ │                  │   │
│  │                    └─────────┬─────────┘                  │   │
│  │                              │                            │   │
│  │                    ┌─────────▼─────────┐                  │   │
│  │                    │   Model Evaluator  │                  │   │
│  │                    │                    │                  │   │
│  │                    │ • MAE              │                  │   │
│  │                    │ • RMSE             │                  │   │
│  │                    │ • MAPE             │                  │   │
│  │                    │ • R-squared        │                  │   │
│  │                    └─────────┬─────────┘                  │   │
│  │                              │                            │   │
│  │                    ┌─────────▼─────────┐                  │   │
│  │                    │    Predictor       │                  │   │
│  │                    │                    │                  │   │
│  │                    │ • Point forecasts  │                  │   │
│  │                    │ • Confidence int.  │                  │   │
│  │                    │ • Multi-step       │                  │   │
│  │                    └───────────────────┘                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
├──────────────────────────────┼───────────────────────────────────┤
│                      DATA LAYER                                  │
│                              │                                   │
│  ┌───────────────────────────┼──────────────────────────────┐   │
│  │              PostgreSQL Database                          │   │
│  │                                                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │  users   │ │products  │ │  sales   │ │ categories │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │suppliers │ │inventory │ │forecasts │ │   alerts   │  │   │
│  │  │          │ │trans.    │ │          │ │            │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  │  ┌──────────┐ ┌──────────────────┐                       │   │
│  │  │  model   │ │dataset_uploads   │                       │   │
│  │  │ _results │ │                  │                       │   │
│  │  └──────────┘ └──────────────────┘                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              File System                                  │   │
│  │                                                           │   │
│  │  data/raw/          - Raw uploaded datasets               │   │
│  │  data/processed/    - Cleaned/processed data              │   │
│  │  models/            - Trained model artifacts (pickle)    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Descriptions

### 2.1 Frontend (React)

| Component | File | Description |
|-----------|------|-------------|
| **Login** | `src/pages/Login.js` | JWT authentication, token storage |
| **Dashboard** | `src/pages/Dashboard.js` | KPI cards, charts, real-time stats |
| **Products** | `src/pages/Products.js` | CRUD operations, search, filter |
| **Inventory** | `src/pages/Inventory.js` | Stock levels, transaction history |
| **Sales** | `src/pages/Sales.js` | Record sales, CSV upload, history |
| **Forecast** | `src/pages/Forecast.js` | Model training, prediction display |
| **What-If** | `src/pages/WhatIf.js` | Scenario simulation interface |
| **Alerts** | `src/pages/Alerts.js` | Alert list, severity filtering |

#### Chart Components
| Component | Description |
|-----------|-------------|
| `DemandForecastChart.js` | Line chart with confidence bands |
| `SalesTrendChart.js` | Daily/weekly sales trends |
| `InventoryLevelChart.js` | Stock level bar chart |
| `TopProductsChart.js` | Horizontal bar chart of top sellers |
| `CategorySalesChart.js` | Pie/donut chart of category breakdown |

#### API Client (`src/services/api.js`)
- Axios instance with `baseURL` configuration
- **Request interceptor**: Injects JWT token from localStorage
- **Response interceptor**: Redirects to login on 401 errors

### 2.2 Backend (FastAPI)

#### API Routers
| Router | Prefix | Description |
|--------|--------|-------------|
| `auth.py` | `/api/auth` | User registration, login, JWT |
| `products.py` | `/api/products` | Product/category/supplier CRUD |
| `inventory.py` | `/api/inventory` | Transaction recording, stock adjustment |
| `sales.py` | `/api/sales` | Sale recording, CSV upload |
| `forecast.py` | `/api/forecast` | ML model training, prediction, what-if |
| `alerts.py` | `/api/alerts` | Alert management |
| `dashboard.py` | `/api/dashboard` | Aggregated statistics |

#### Services Layer
| Service | Responsibility |
|---------|----------------|
| `auth_service.py` | Password hashing, JWT creation, user lookup |
| `product_service.py` | Product CRUD business logic |
| `inventory_service.py` | Stock calculation, transaction processing |
| `sales_service.py` | Sale recording, stock deduction, CSV parsing |
| `forecast_service.py` | Data preparation, model training, forecasting |
| `alert_service.py` | Alert generation based on stock/demand rules |
| `dashboard_service.py` | KPI aggregation, trend calculations |

#### Schemas (Pydantic)
Request/response validation using Pydantic v2 models:
- `user.py` - UserCreate, UserResponse, Token
- `product.py` - ProductCreate, ProductResponse, CategoryCreate
- `inventory.py` - TransactionCreate, TransactionResponse
- `sales.py` - SaleCreate, SaleResponse
- `forecast.py` - ForecastRequest, ForecastResponse, WhatIfRequest
- `alert.py` - AlertResponse, AlertSummary
- `dashboard.py` - DashboardStats, SalesTrend, TopProduct

### 2.3 ML Pipeline

#### Data Cleaner (`ml/preprocessing/data_cleaner.py`)
```
Raw Data → Handle Missing Values → Remove Duplicates → Validate Dates → Clip Outliers → Clean Data
```

#### Feature Builder (`ml/feature_engineering/feature_builder.py`)
```
Clean Data → Time Features → Lag Features → Rolling Features → Calendar Features → Demand Features → Feature Matrix
```

#### Model Trainer (`ml/training/model_trainer.py`)
```
Feature Matrix → Train 6 Models → Compare on Validation Set → Select Best → Save to Disk
```

#### Model Evaluator (`ml/evaluation/metrics.py`)
```
Predictions → Calculate MAE, RMSE, MAPE, R² → Comparison Table → Rank Models
```

#### Predictor (`ml/forecasting/predictor.py`)
```
Trained Model + Features → Point Predictions → Confidence Intervals → Forecast Output
```

---

## 3. Data Flow

### 3.1 User Authentication Flow
```
User → Login Page → POST /api/auth/login → Backend validates credentials
  → Returns JWT token → Frontend stores in localStorage
  → All subsequent requests include Bearer token
  → Backend validates token on each request
```

### 3.2 Sales Recording Flow
```
User → Sales Page → POST /api/sales/ → Backend validates product exists
  → Checks sufficient stock → Creates Sale record
  → Deducts stock from Product → Returns SaleResponse
```

### 3.3 ML Forecasting Flow
```
User → Forecast Page → POST /api/forecast/train (with product_id, model_type)
  → Backend fetches sales history for product
  → DataCleaner: clean raw data
  → FeatureBuilder: create features (time, lag, rolling, calendar, demand)
  → ModelTrainer: train specified model
  → ModelEvaluator: evaluate on validation set
  → Save model to disk + store metrics in model_results table
  → Return metrics to frontend

User → POST /api/forecast/predict (with product_id, periods, model_type)
  → Backend loads trained model
  → Predictor generates forecasts with confidence intervals
  → Returns list of {date, forecasted_quantity, lower_bound, upper_bound}
```

### 3.4 Dashboard Data Flow
```
User → Dashboard Page → GET /api/dashboard/stats
  → DashboardService aggregates from multiple tables:
    - Product count, low stock count
    - Today's sales total, month's sales total
    - Transaction count, active alert count
    - Total inventory value
  → Returns DashboardStats

User → Dashboard Page → GET /api/dashboard/sales-trends?days=30
  → DashboardService queries Sales table
  → Groups by date, sums quantities and revenue
  → Returns daily trend data for charting
```

### 3.5 What-If Analysis Flow
```
User → What-If Page → POST /api/forecast/what-if
  → Backend generates baseline forecast
  → Applies adjustment factors (price, seasonality, trend)
  → Returns both baseline and adjusted forecasts
  → Frontend displays comparison chart
```

---

## 4. ML Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ML PIPELINE                               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 1. DATA COLLECTION                                     │ │
│  │    • Query Sales table for product_id                  │ │
│  │    • Filter by date range                              │ │
│  │    • Aggregate to daily level                          │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 2. DATA CLEANING                                       │ │
│  │    • Handle missing values (median/mode imputation)    │ │
│  │    • Remove duplicate rows                             │ │
│  │    • Validate and parse dates                          │ │
│  │    • Detect and clip outliers (IQR method)             │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 3. FEATURE ENGINEERING                                 │ │
│  │    • Time features (day, week, month, quarter, etc.)   │ │
│  │    • Lag features (1, 7, 14, 30 days)                  │ │
│  │    • Rolling statistics (mean, std for 7, 14, 30 days) │ │
│  │    • Calendar features (holidays, month boundaries)     │ │
│  │    • Demand features (previous period values)          │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 4. TRAIN/VALIDATION SPLIT                              │ │
│  │    • Time-based split (80% train, 20% validation)      │ │
│  │    • No random shuffling (preserves temporal order)    │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 5. MODEL TRAINING                                      │ │
│  │    • Linear Regression (baseline)                      │ │
│  │    • Random Forest (n_estimators=100)                  │ │
│  │    • XGBoost (n_estimators=100, lr=0.1)               │ │
│  │    • LightGBM (n_estimators=100, lr=0.1)              │ │
│  │    • LSTM (64→32 units, 30-day lookback)               │ │
│  │    • Prophet (yearly + weekly seasonality)             │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 6. MODEL EVALUATION                                    │ │
│  │    • MAE (Mean Absolute Error)                         │ │
│  │    • RMSE (Root Mean Squared Error)                    │ │
│  │    • MAPE (Mean Absolute Percentage Error)             │ │
│  │    • R² (Coefficient of Determination)                 │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 7. BEST MODEL SELECTION                                │ │
│  │    • Select model with lowest RMSE                     │ │
│  │    • Save model artifacts to disk                      │ │
│  │    • Store metrics in model_results table              │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │ 8. FORECASTING                                         │ │
│  │    • Load trained model                                │ │
│  │    • Generate predictions for N periods                │ │
│  │    • Calculate confidence intervals (95%)              │ │
│  │    • Return forecasts with date, quantity, bounds      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Database Schema

### Entity Relationship Diagram (Text)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    users     │     │  categories  │     │  suppliers   │
│──────────────│     │──────────────│     │──────────────│
│ id (PK)      │     │ id (PK)      │     │ id (PK)      │
│ username     │     │ name         │     │ name         │
│ email        │     │ description  │     │ contact_name │
│ hashed_pwd   │     │ created_at   │     │ email        │
│ role         │     └──────┬───────┘     │ phone        │
│ is_active    │            │             │ address      │
│ created_at   │            │             │ lead_time    │
│ updated_at   │            │             │ created_at   │
└──────┬───────┘            │             └──────┬───────┘
       │                    │                    │
       │                    │  1:N               │  1:N
       │                    └─────────┬──────────┘
       │                              │
       │                    ┌─────────▼──────────┐
       │                    │     products       │
       │                    │────────────────────│
       │                    │ id (PK)            │
       │                    │ name               │
       │                    │ sku (UNIQUE)       │
       │                    │ category_id (FK)   │
       │                    │ supplier_id (FK)   │
       │                    │ price              │
       │                    │ cost_price         │
       │                    │ current_stock      │
       │                    │ minimum_stock      │
       │                    │ safety_stock       │
       │                    │ lead_time_days     │
       │                    │ created_at         │
       │                    │ updated_at         │
       │                    └────┬───┬───┬───┬───┘
       │                         │   │   │   │
       │            ┌────────────┘   │   │   └────────────┐
       │            │                │   │                │
       │   1:N      │    1:N         │   │    1:N         │  1:N
       │            │                │   │                │
┌──────▼───────┐ ┌──▼────────────┐ ┌▼──▼────────┐ ┌─────▼─────────┐
│    sales     │ │  inventory_   │ │  forecasts │ │    alerts     │
│──────────────│ │  transactions │ │────────────│ │───────────────│
│ id (PK)      │ │───────────────│ │ id (PK)    │ │ id (PK)       │
│ date         │ │ id (PK)       │ │ product_id │ │ product_id    │
│ product_id   │ │ product_id    │ │ forecast_  │ │ alert_type    │
│ product_name │ │ transaction_  │ │   date     │ │ severity      │
│ category     │ │   type        │ │ predicted_ │ │ message       │
│ units_sold   │ │ quantity      │ │   demand   │ │ is_read       │
│ selling_price│ │ reference_num │ │ lower_bound│ │ created_at    │
│ promotion    │ │ notes         │ │ upper_bound│ └───────────────┘
│ discount     │ │ created_at    │ │ model_used │
│ holiday      │ └───────────────┘ │ created_at │
│ store_location│                   └────────────┘
│ stock_available│
│ created_at   │    ┌──────────────────┐
└──────────────┘    │  model_results    │
                    │──────────────────│
                    │ id (PK)          │
                    │ model_name       │
                    │ product_id (FK)  │
                    │ mae              │
                    │ rmse             │
                    │ mape             │
                    │ r2_score         │
                    │ is_best_model    │
                    │ trained_at       │
                    │ model_path       │
                    │ parameters       │
                    └──────────────────┘

                    ┌──────────────────┐
                    │ dataset_uploads  │
                    │──────────────────│
                    │ id (PK)          │
                    │ filename         │
                    │ records_count    │
                    │ status           │
                    │ error_message    │
                    │ uploaded_by (FK) │
                    │ created_at       │
                    └──────────────────┘
```

### Table Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| categories → products | One-to-Many | Each category has many products |
| suppliers → products | One-to-Many | Each supplier provides many products |
| products → sales | One-to-Many | Each product has many sales records |
| products → inventory_transactions | One-to-Many | Each product has many stock movements |
| products → forecasts | One-to-Many | Each product has many forecast records |
| products → alerts | One-to-Many | Each product can generate many alerts |
| users → dataset_uploads | One-to-Many | Each user can upload many datasets |

### Indexes

| Table | Indexed Columns | Purpose |
|-------|----------------|---------|
| users | id, username, email | Fast user lookup |
| products | id, sku | Fast SKU lookup |
| sales | id, date | Fast date-range queries |
| inventory_transactions | id | Primary key lookup |
| forecasts | id | Primary key lookup |
| alerts | id | Primary key lookup |
| categories | id | Primary key lookup |
| suppliers | id | Primary key lookup |

---

## 6. Security Architecture

### Authentication Flow
```
1. User submits credentials → POST /api/auth/login
2. Backend verifies username + password (bcrypt)
3. JWT token created with username + expiry
4. Token returned to frontend
5. Frontend stores token in localStorage
6. All API requests include: Authorization: Bearer <token>
7. Backend validates JWT on each protected request
```

### Password Security
- Passwords hashed using bcrypt via passlib
- Salt generated automatically per password
- No plaintext passwords stored or logged

### JWT Configuration
- Algorithm: HS256
- Expiry: 30 minutes (configurable)
- Claims: `sub` (username), `exp` (expiration)

### API Security
- CORS configured (restrict in production)
- Global exception handler prevents error message leaks
- Input validation via Pydantic schemas
- SQL injection prevented by SQLAlchemy ORM
