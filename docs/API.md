# API Reference

Base URL: `http://localhost:8000/api`

All authenticated endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Authentication

### POST `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

**Errors:**
| Status | Detail |
|--------|--------|
| 400 | Username already registered |
| 400 | Email already registered |
| 422 | Validation error |

---

### POST `/api/auth/login`

Authenticate and receive a JWT access token.

**Request Body (form-data):**
| Field | Type | Required |
|-------|------|----------|
| username | string | Yes |
| password | string | Yes |

**Request Example:**
```
username=johndoe&password=securepassword123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
| Status | Detail |
|--------|--------|
| 401 | Incorrect username or password |

---

### GET `/api/auth/me`

Get the currently authenticated user's information.

**Headers:**
| Header | Value |
|--------|-------|
| Authorization | Bearer `<token>` |

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

---

## Products

### GET `/api/products/`

List all products with pagination and filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Number of records to skip |
| limit | int | 20 | Max records to return (1-100) |
| category_id | int | - | Filter by category ID |
| supplier_id | int | - | Filter by supplier ID |
| search | string | - | Search by product name |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Wireless Mouse",
      "sku": "WM-001",
      "description": "Ergonomic wireless mouse",
      "category_id": 1,
      "supplier_id": 1,
      "cost_price": 12.50,
      "selling_price": 29.99,
      "current_stock": 150,
      "minimum_stock": 20,
      "unit": "pcs"
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

---

### POST `/api/products/`

Create a new product.

**Request Body:**
```json
{
  "name": "Wireless Mouse",
  "sku": "WM-001",
  "description": "Ergonomic wireless mouse",
  "category_id": 1,
  "supplier_id": 1,
  "cost_price": 12.50,
  "selling_price": 29.99,
  "current_stock": 150,
  "minimum_stock": 20,
  "unit": "pcs"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "sku": "WM-001",
  "cost_price": 12.50,
  "selling_price": 29.99,
  "current_stock": 150,
  "minimum_stock": 20
}
```

**Errors:**
| Status | Detail |
|--------|--------|
| 400 | SKU already exists |
| 422 | Validation error |

---

### GET `/api/products/{product_id}`

Get a single product by ID.

**Response (200 OK):** Product object (same as above)

**Errors:**
| Status | Detail |
|--------|--------|
| 404 | Product not found |

---

### PUT `/api/products/{product_id}`

Update a product. Only provided fields are updated.

**Request Body (all fields optional):**
```json
{
  "name": "Updated Product Name",
  "selling_price": 34.99,
  "minimum_stock": 25
}
```

**Response (200 OK):** Updated product object

---

### DELETE `/api/products/{product_id}`

Delete a product.

**Response:** `204 No Content`

**Errors:**
| Status | Detail |
|--------|--------|
| 404 | Product not found |

---

### GET `/api/products/categories/`

List all product categories.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  },
  {
    "id": 2,
    "name": "Clothing",
    "description": "Apparel and accessories"
  }
]
```

---

### POST `/api/products/categories/`

Create a new category.

**Request Body:**
```json
{
  "name": "Electronics",
  "description": "Electronic devices and accessories"
}
```

---

### GET `/api/products/suppliers/`

List all suppliers.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Tech Supplies Inc.",
    "contact_person": "Jane Smith",
    "email": "jane@techsupplies.com",
    "phone": "+1-555-0100",
    "address": "123 Tech Street"
  }
]
```

---

### POST `/api/products/suppliers/`

Create a new supplier.

**Request Body:**
```json
{
  "name": "Tech Supplies Inc.",
  "contact_person": "Jane Smith",
  "email": "jane@techsupplies.com",
  "phone": "+1-555-0100",
  "address": "123 Tech Street"
}
```

---

## Inventory

### POST `/api/inventory/transactions`

Record an inventory transaction (inbound, outbound, or adjustment).

**Request Body:**
```json
{
  "product_id": 1,
  "transaction_type": "inbound",
  "quantity": 100,
  "unit_price": 12.50,
  "reference_number": "PO-2024-001",
  "notes": "Restocking from supplier"
}
```

**Transaction Types:**
| Type | Effect on Stock |
|------|-----------------|
| `inbound` | Increases stock by quantity |
| `outbound` | Decreases stock by quantity |
| `adjustment` | Sets stock to quantity |

**Response (201 Created):**
```json
{
  "id": 1,
  "product_id": 1,
  "transaction_type": "inbound",
  "quantity": 100,
  "unit_price": 12.50,
  "reference_number": "PO-2024-001",
  "notes": "Restocking from supplier",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
| Status | Detail |
|--------|--------|
| 400 | Insufficient stock (for outbound) |
| 404 | Product not found |

---

### GET `/api/inventory/transactions`

Get inventory transaction history.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| product_id | int | - | Filter by product |
| transaction_type | string | - | Filter by type |
| skip | int | 0 | Pagination offset |
| limit | int | 20 | Page size |

**Response (200 OK):** Array of transaction objects

---

### GET `/api/inventory/summary`

Get inventory summary for all products.

**Response (200 OK):**
```json
[
  {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "current_stock": 150,
    "minimum_stock": 20,
    "total_inbound": 500,
    "total_outbound": 350,
    "net_movement": 150
  }
]
```

---

### PUT `/api/inventory/adjust/{product_id}`

Manually adjust stock level for a product.

**Request Body:**
```json
{
  "new_stock": 200,
  "notes": "Annual inventory count adjustment"
}
```

**Response (200 OK):** Transaction object with type "adjustment"

---

## Sales

### GET `/api/sales/`

List sales with pagination and date/product filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Pagination offset |
| limit | int | 20 | Page size |
| start_date | date | - | Filter from date (YYYY-MM-DD) |
| end_date | date | - | Filter to date (YYYY-MM-DD) |
| product_id | int | - | Filter by product |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 5,
      "unit_price": 29.99,
      "total_price": 149.95,
      "discount": 0.0,
      "notes": null,
      "sale_date": "2024-01-15T14:30:00Z",
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 120,
  "skip": 0,
  "limit": 20
}
```

---

### POST `/api/sales/`

Record a new sale. Automatically deducts stock.

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 5,
  "unit_price": 29.99,
  "discount": 0.0,
  "notes": "Bulk order"
}
```

**Response (201 Created):** Sale object

**Errors:**
| Status | Detail |
|--------|--------|
| 400 | Insufficient stock |
| 404 | Product not found |

---

### POST `/api/sales/upload-csv`

Bulk upload sales from a CSV file.

**Request:** `multipart/form-data` with field `file`

**CSV Format:**
```csv
product_id,quantity,unit_price,discount,notes
1,5,29.99,0.0,Bulk order
2,3,49.99,5.0,Promotional
```

**Required Columns:** `product_id`, `quantity`, `unit_price`
**Optional Columns:** `discount`, `notes`

**Response (201 Created):**
```json
{
  "created": 2,
  "errors": [
    "Row 3: Product not found",
    "Row 5: Insufficient stock"
  ]
}
```

---

## Forecasting

### POST `/api/forecast/train`

Train an ML model for a specific product.

**Request Body:**
```json
{
  "product_id": 1,
  "model_type": "random_forest"
}
```

**Supported Model Types:**
| Value | Model |
|-------|-------|
| `linear_regression` | Linear Regression |
| `random_forest` | Random Forest |
| `xgboost` | XGBoost |
| `lightgbm` | LightGBM |
| `lstm` | LSTM Neural Network |
| `prophet` | Facebook Prophet |

**Response (200 OK):**
```json
{
  "product_id": 1,
  "model_type": "random_forest",
  "status": "trained",
  "metrics": {
    "mae": 2.34,
    "rmse": 3.12,
    "mape": 8.5,
    "r2": 0.89
  }
}
```

---

### POST `/api/forecast/predict`

Generate a demand forecast for a product.

**Request Body:**
```json
{
  "product_id": 1,
  "periods": 30,
  "model_type": "random_forest"
}
```

**Response (200 OK):**
```json
{
  "product_id": 1,
  "model_type": "random_forest",
  "forecasts": [
    {
      "date": "2024-02-01",
      "forecasted_quantity": 45,
      "lower_bound": 38,
      "upper_bound": 52
    },
    {
      "date": "2024-02-02",
      "forecasted_quantity": 42,
      "lower_bound": 35,
      "upper_bound": 49
    }
  ]
}
```

---

### GET `/api/forecast/compare/{product_id}`

Compare all available models for a product.

**Response (200 OK):**
```json
{
  "product_id": 1,
  "models": [
    {
      "model_name": "linear_regression",
      "mae": 4.21,
      "rmse": 5.67,
      "r2": 0.72
    },
    {
      "model_name": "random_forest",
      "mae": 2.34,
      "rmse": 3.12,
      "r2": 0.89
    },
    {
      "model_name": "xgboost",
      "mae": 2.18,
      "rmse": 2.95,
      "r2": 0.91
    }
  ],
  "best_model": "xgboost"
}
```

---

### POST `/api/forecast/what-if`

Run what-if scenario analysis.

**Request Body:**
```json
{
  "product_id": 1,
  "price_change_pct": -10.0,
  "seasonality_factor": 1.5,
  "trend_factor": 1.1
}
```

**Response (200 OK):**
```json
{
  "product_id": 1,
  "baseline_forecast": [
    {"date": "2024-02-01", "forecasted_quantity": 45},
    {"date": "2024-02-02", "forecasted_quantity": 42}
  ],
  "adjusted_forecast": [
    {"date": "2024-02-01", "forecasted_quantity": 58},
    {"date": "2024-02-02", "forecasted_quantity": 54}
  ],
  "parameters": {
    "price_change_pct": -10.0,
    "seasonality_factor": 1.5,
    "trend_factor": 1.1
  }
}
```

---

### GET `/api/forecast/reorder-recommendations`

Get AI-driven reorder recommendations for all low-stock products.

**Response (200 OK):**
```json
[
  {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "current_stock": 8,
    "reorder_quantity": 32,
    "estimated_stockout_date": "2024-02-05",
    "priority": "high"
  },
  {
    "product_id": 3,
    "product_name": "USB Cable",
    "current_stock": 0,
    "reorder_quantity": 50,
    "estimated_stockout_date": null,
    "priority": "critical"
  }
]
```

**Priority Levels:**
| Priority | Condition |
|----------|-----------|
| `critical` | Stock is zero |
| `high` | Stock <= 50% of minimum |
| `medium` | Stock <= minimum |

---

## Alerts

### GET `/api/alerts/`

List alerts with optional filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| is_read | bool | - | Filter by read status |
| severity | string | - | Filter by severity level |
| skip | int | 0 | Pagination offset |
| limit | int | 20 | Page size |

**Severity Levels:** `low`, `medium`, `high`, `critical`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "alert_type": "low_stock",
    "message": "Stock level for Wireless Mouse is below minimum threshold",
    "severity": "high",
    "product_id": 1,
    "is_read": false,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

---

### PUT `/api/alerts/{alert_id}/read`

Mark an alert as read.

**Response (200 OK):** Updated alert object

---

### GET `/api/alerts/summary`

Get alert count summary by severity.

**Response (200 OK):**
```json
{
  "total": 45,
  "unread": 12,
  "critical": 2,
  "high": 5,
  "medium": 3,
  "low": 2
}
```

---

### GET `/api/alerts/product/{product_id}`

Get all alerts for a specific product.

**Response (200 OK):** Array of alert objects

---

## Dashboard

### GET `/api/dashboard/stats`

Get KPI summary statistics.

**Response (200 OK):**
```json
{
  "total_products": 120,
  "low_stock_products": 8,
  "total_sales_today": 1250.00,
  "total_sales_month": 45000.00,
  "total_transactions": 342,
  "active_alerts": 12,
  "total_inventory_value": 125000.00
}
```

---

### GET `/api/dashboard/sales-trends`

Get daily sales trends.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | int | 30 | Number of days (1-365) |

**Response (200 OK):**
```json
[
  {
    "date": "2024-01-15",
    "total_sales": 1250.00,
    "total_quantity": 42
  },
  {
    "date": "2024-01-16",
    "total_sales": 980.50,
    "total_quantity": 35
  }
]
```

---

### GET `/api/dashboard/category-sales`

Get sales breakdown by category.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | int | 30 | Number of days (1-365) |

**Response (200 OK):**
```json
[
  {
    "category_name": "Electronics",
    "total_sales": 25000.00,
    "total_quantity": 450
  },
  {
    "category_name": "Clothing",
    "total_sales": 18000.00,
    "total_quantity": 320
  }
]
```

---

### GET `/api/dashboard/top-products`

Get top selling products by revenue.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | int | 30 | Number of days (1-365) |
| limit | int | 10 | Max products to return (1-50) |

**Response (200 OK):**
```json
[
  {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "total_quantity_sold": 150,
    "total_revenue": 4498.50
  }
]
```

---

### GET `/api/dashboard/inventory-trends`

Get inbound/outbound inventory movement trends.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | int | 30 | Number of days (1-365) |

**Response (200 OK):**
```json
[
  {
    "date": "2024-01-15",
    "inbound": 200,
    "outbound": 150
  }
]
```

---

## Utility

### GET `/`

API root information.

**Response (200 OK):**
```json
{
  "message": "AI-Powered Inventory Management & Demand Forecasting System",
  "docs": "/docs",
  "version": "1.0.0"
}
```

### GET `/health`

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created successfully |
| 204 | Deleted successfully (no content) |
| 400 | Bad request (validation error, business rule violation) |
| 401 | Unauthorized (invalid or missing token) |
| 404 | Resource not found |
| 422 | Unprocessable entity (request body validation failed) |
| 500 | Internal server error |

### Error Response Format
```json
{
  "detail": "Error message describing the problem"
}
```
