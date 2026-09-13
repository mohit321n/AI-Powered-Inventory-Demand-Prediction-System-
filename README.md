<div align="center">

# AI-Powered Inventory Management & Demand Forecasting System

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)

**A full-stack AI/ML application that predicts future demand, monitors inventory, and generates intelligent reorder recommendations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                               │
│                   Dashboard │ Charts │ What-If                      │
│                         (Port 3000)                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────────────┐
│                       FASTAPI BACKEND                               │
│                    (Port 8000) │ Swagger Docs                       │
├────────────┬───────────────┬───────────────┬───────────────────────┤
│  Auth API  │ Product API   │  Sales API    │   Forecast API        │
│  JWT+bcrypt│ CRUD + Search │ CSV Upload    │   ML Training         │
├────────────┴───────────────┴───────────────┴───────────────────────┤
│                       SERVICE LAYER                                 │
│  auth │ product │ inventory │ sales │ forecast │ alert │ dashboard │
├─────────────────────────────┬───────────────────────────────────────┤
│      PostgreSQL Database    │         ML Pipeline                   │
│  users │ products │ sales   │  Clean → Features → Train → Predict  │
│  categories │ suppliers     │  Linear │ RF │ XGBoost │ LSTM        │
│  inventory │ forecasts      │  LightGBM │ Prophet │ Evaluation     │
│  alerts │ model_results     │  MAE │ RMSE │ MAPE │ R²              │
└─────────────────────────────┴───────────────────────────────────────┘
```

---

## Key Features

<table>
<tr>
<td width="50%">

### Core Functionality
- **Product Management** - Full CRUD for products, categories, suppliers
- **Inventory Tracking** - Real-time stock with transaction history
- **Sales Recording** - Manual entry + CSV bulk upload with validation
- **Alert System** - Low stock, stockout risk, overstock warnings

</td>
<td width="50%">

### AI/ML Capabilities
- **Demand Forecasting** - 6 ML models with automatic best selection
- **Model Comparison** - Side-by-side evaluation with metrics table
- **What-If Analysis** - Simulate demand, lead time, and promotion changes
- **Reorder Recommendations** - AI-driven reorder points + EOQ

</td>
</tr>
<tr>
<td>

### Dashboard & Analytics
- **KPI Dashboard** - Total products, inventory value, alerts
- **Sales Trends** - Daily/weekly/monthly visualizations
- **Category Breakdown** - Pie charts for category-wise sales
- **Top Products** - Best and worst performing products

</td>
<td>

### Enterprise Features
- **JWT Authentication** - Secure login with bcrypt hashing
- **Role-Based Access** - Admin and user roles
- **Input Validation** - Pydantic schemas for all endpoints
- **Docker Deployment** - One-command production setup

</td>
</tr>
</table>

---

## Tech Stack

<table>
<tr><th>Layer</th><th>Technology</th><th>Purpose</th></tr>
<tr><td>Frontend</td><td>React 18 + Material UI</td><td>Professional dark-themed SPA</td></tr>
<tr><td>Charts</td><td>Chart.js + react-chartjs-2</td><td>Interactive visualizations</td></tr>
<tr><td>Backend</td><td>FastAPI + SQLAlchemy</td><td>High-performance async API</td></tr>
<tr><td>Database</td><td>PostgreSQL 15</td><td>Relational data storage</td></tr>
<tr><td>Auth</td><td>JWT + bcrypt</td><td>Secure authentication</td></tr>
<tr><td>ML</td><td>scikit-learn, XGBoost, LightGBM</td><td>Traditional ML models</td></tr>
<tr><td>DL</td><td>TensorFlow/Keras</td><td>LSTM time-series model</td></tr>
<tr><td>Forecast</td><td>Prophet</td><td>Seasonality decomposition</td></tr>
<tr><td>Data</td><td>pandas, NumPy</td><td>Data processing</td></tr>
<tr><td>Deploy</td><td>Docker Compose</td><td>Containerized deployment</td></tr>
</table>

---

## Project Structure

```
Project2/
├── backend/
│   ├── app/
│   │   ├── api/                     # 7 API routers
│   │   │   ├── auth.py              # Register, login, JWT
│   │   │   ├── products.py          # CRUD + categories + suppliers
│   │   │   ├── inventory.py         # Transactions + adjustments
│   │   │   ├── sales.py             # Sales + CSV upload
│   │   │   ├── forecast.py          # ML train + predict + what-if
│   │   │   ├── alerts.py            # Alert management
│   │   │   └── dashboard.py         # KPI + analytics
│   │   ├── models/models.py         # 10 SQLAlchemy models
│   │   ├── schemas/                 # 8 Pydantic schemas
│   │   ├── services/                # 7 business logic modules
│   │   ├── database/database.py     # DB connection
│   │   ├── config.py                # Environment config
│   │   └── main.py                  # FastAPI entry point
│   ├── ml/                          # Machine Learning Pipeline
│   │   ├── preprocessing/           # Data cleaning
│   │   ├── feature_engineering/     # 20+ engineered features
│   │   ├── training/                # 6 model trainers
│   │   ├── evaluation/              # MAE, RMSE, MAPE, R²
│   │   └── forecasting/             # Predictor + confidence
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/                   # 8 page components
│   │   ├── charts/                  # 5 chart components
│   │   ├── services/api.js          # Axios client
│   │   └── App.js                   # Router + theme
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── raw/                         # Uploaded datasets
│   └── processed/                   # Cleaned data
├── tests/                           # 88 test cases
├── docs/                            # 6 documentation files
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and start everything
git clone <repo-url>
cd Project2
docker-compose up --build
```

### Option 2: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Database
psql -U postgres -c "CREATE DATABASE inventory_db;"

# Configure
cp .env.example .env            # Edit with your credentials

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm start
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## ML Pipeline

### Data Flow

```
Historical Sales Data
    → Data Cleaning (missing values, duplicates, outliers)
    → Feature Engineering (20+ features)
    → Time-Series Train/Val/Test Split
    → Model Training (6 models)
    → Evaluation (MAE, RMSE, MAPE, R²)
    → Best Model Selection (lowest RMSE)
    → Future Demand Prediction
    → Inventory Optimization
    → Reorder Recommendations
    → Dashboard & Alerts
```

### Models Implemented

| Model | Type | Strengths |
|-------|------|-----------|
| Linear Regression | Linear | Baseline, interpretable |
| Random Forest | Ensemble | Handles non-linearity |
| XGBoost | Gradient Boosting | High accuracy, tabular data |
| LightGBM | Gradient Boosting | Fast training, large datasets |
| LSTM | Deep Learning | Sequential patterns |
| Prophet | Time-series | Seasonality & trends |

### Feature Engineering (20+ Features)

| Feature Category | Features | Purpose |
|-----------------|----------|---------|
| Time | day, week, month, quarter, year, day_of_week, is_weekend | Temporal patterns |
| Lag | lag_1, lag_7, lag_14, lag_30 | Autoregressive signals |
| Rolling | rolling_mean_7/14/30, rolling_std_7/14/30 | Trend & volatility |
| Calendar | is_holiday, is_month_start/end, is_promotion | External effects |
| Demand | prev_month_demand, prev_year_demand, prev_month_avg | Historical comparison |

### Evaluation Metrics

| Metric | What It Measures |
|--------|-----------------|
| MAE | Average absolute prediction error |
| RMSE | Penalizes large errors more heavily |
| MAPE | Percentage error (0-100%) |
| R² | Variance explained by the model |

---

## API Reference

<details>
<summary><strong>Authentication</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Get current user |

</details>

<details>
<summary><strong>Products</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List (paginated, searchable) |
| POST | `/api/products/` | Create product |
| GET | `/api/products/{id}` | Get by ID |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| GET/POST | `/api/products/categories/` | List/Create categories |
| GET/POST | `/api/products/suppliers/` | List/Create suppliers |

</details>

<details>
<summary><strong>Inventory</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/inventory/transactions` | Record transaction |
| GET | `/api/inventory/transactions` | Transaction history |
| GET | `/api/inventory/summary` | Stock summary per product |
| PUT | `/api/inventory/adjust/{id}` | Manual stock adjustment |

</details>

<details>
<summary><strong>Sales</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sales/` | List (filterable by date/product) |
| POST | `/api/sales/` | Record sale |
| POST | `/api/sales/upload-csv` | Bulk CSV upload |

</details>

<details>
<summary><strong>Forecasting</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/forecast/train` | Train ML models |
| POST | `/api/forecast/predict` | Generate forecast |
| GET | `/api/forecast/compare/{id}` | Model comparison |
| POST | `/api/forecast/what-if` | Scenario analysis |
| GET | `/api/forecast/reorder-recommendations` | AI reorder suggestions |

</details>

<details>
<summary><strong>Alerts & Dashboard</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/` | List alerts |
| PUT | `/api/alerts/{id}/read` | Mark as read |
| GET | `/api/alerts/summary` | Alert counts by severity |
| GET | `/api/dashboard/stats` | KPI statistics |
| GET | `/api/dashboard/sales-trends` | Sales over time |
| GET | `/api/dashboard/category-sales` | Category breakdown |
| GET | `/api/dashboard/top-products` | Best/worst products |
| GET | `/api/dashboard/inventory-trends` | Stock movement |

</details>

---

## Screenshots

> Run the application to see the live dashboard.

| Dashboard | Forecast | What-If Analysis |
|-----------|----------|------------------|
| KPI cards, sales trends, top products | Historical vs predicted demand with confidence bands | Simulate demand changes, lead time adjustments |
| ![Dashboard](docs/screenshots/dashboard.png) | ![Forecast](docs/screenshots/forecast.png) | ![What-If](docs/screenshots/whatif.png) |

---

## Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | Complete endpoint documentation |
| [ML Methodology](docs/ML_METHODOLOGY.md) | Pipeline, models, evaluation |
| [Dataset Guide](docs/DATASET.md) | Sources, formats, limitations |
| [Deployment Guide](docs/DEPLOYMENT.md) | Docker + manual setup |
| [Architecture](docs/ARCHITECTURE.md) | System design & data flow |

---

## Testing

```bash
cd backend
pytest tests/ -v
```

**88 test cases** covering:
- Authentication (register, login, JWT)
- Product CRUD operations
- Inventory transactions & adjustments
- Sales recording & CSV upload
- ML pipeline (cleaning, features, training, evaluation)
- Reorder calculations (safety stock, EOQ, reorder point)
- Data validation (missing values, duplicates, dates)

---

## Dataset

The system includes a **sample dataset generator** producing 5,000 realistic retail records.

### Custom CSV Upload Format

```csv
date,product_id,product_name,category,units_sold,selling_price,promotion,discount,holiday,store_location,stock_available
2024-01-15,1,Laptop Pro,Electronics,5,1299.99,true,10,false,New York,45
2024-01-15,2,Wireless Mouse,Electronics,20,29.99,false,0,false,New York,180
```

See [docs/DATASET.md](docs/DATASET.md) for recommended public datasets.

---

## License

This project is licensed under the MIT License.

---

<div align="center">

**Built with Python + React + AI/ML**

</div>
