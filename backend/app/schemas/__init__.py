from .alert import AlertResponse, AlertSummary
from .dashboard import CategorySales, DashboardStats, SalesTrend, TopProduct
from .forecast import (
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    ModelComparisonItem,
    ModelComparisonResponse,
    ReorderRecommendation,
    WhatIfRequest,
    WhatIfResponse,
)
from .inventory import (
    InventorySummary,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
)
from .product import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    SupplierCreate,
    SupplierResponse,
)
from .sales import (
    DatasetUploadResponse,
    SaleCreate,
    SaleResponse,
)
from .user import Token, UserCreate, UserLogin, UserResponse

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "CategoryCreate",
    "CategoryResponse",
    "SupplierCreate",
    "SupplierResponse",
    # Inventory
    "InventoryTransactionCreate",
    "InventoryTransactionResponse",
    "InventorySummary",
    # Sales
    "SaleCreate",
    "SaleResponse",
    "DatasetUploadResponse",
    # Forecast
    "ForecastRequest",
    "ForecastPoint",
    "ForecastResponse",
    "ModelComparisonItem",
    "ModelComparisonResponse",
    "ReorderRecommendation",
    "WhatIfRequest",
    "WhatIfResponse",
    # Alert
    "AlertResponse",
    "AlertSummary",
    # Dashboard
    "DashboardStats",
    "SalesTrend",
    "CategorySales",
    "TopProduct",
]
