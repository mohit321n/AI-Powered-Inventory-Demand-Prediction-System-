from datetime import date, datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_user
from app.models import Sale, Product, User, DatasetUpload

router = APIRouter(prefix="/sales", tags=["sales"])


class SaleCreate(BaseModel):
    product_id: int
    units_sold: int
    selling_price: float
    promotion: bool = False
    discount: float = 0.0
    holiday: bool = False
    store_location: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    date: datetime
    product_id: int
    product_name: Optional[str]
    category: Optional[str]
    units_sold: int
    selling_price: float
    promotion: bool
    discount: float
    holiday: bool
    store_location: Optional[str]
    stock_available: Optional[int]

    class Config:
        from_attributes = True


class PaginatedSales(BaseModel):
    items: list[SaleResponse]
    total: int
    skip: int
    limit: int


@router.get("/", response_model=PaginatedSales)
def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    product_id: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Sale)
    if start_date:
        query = query.filter(Sale.date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Sale.date <= datetime.combine(end_date, datetime.max.time()))
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if category:
        query = query.filter(Sale.category == category)
    total = query.count()
    items = query.order_by(Sale.date.desc()).offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.current_stock < sale.units_sold:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    product.current_stock -= sale.units_sold

    db_sale = Sale(
        date=datetime.now(),
        product_id=sale.product_id,
        product_name=product.name,
        category=product.category.name if product.category else None,
        units_sold=sale.units_sold,
        selling_price=sale.selling_price,
        promotion=sale.promotion,
        discount=sale.discount,
        holiday=sale.holiday,
        store_location=sale.store_location,
        stock_available=product.current_stock,
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.post("/upload-csv", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_sales_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        df = pd.read_csv(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    required_columns = ["date", "product_id", "units_sold", "selling_price"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    created = 0
    errors = []

    upload_record = DatasetUpload(
        filename=file.filename,
        uploaded_by=current_user.id,
        status="processing",
    )
    db.add(upload_record)
    db.commit()

    for idx, row in df.iterrows():
        try:
            product = db.query(Product).filter(Product.id == int(row["product_id"])).first()
            if not product:
                errors.append(f"Row {idx + 1}: Product not found")
                continue

            sale_date = pd.to_datetime(row["date"])
            promotion = bool(row.get("promotion", False))
            discount = float(row.get("discount", 0))
            holiday = bool(row.get("holiday", False))

            db_sale = Sale(
                date=sale_date,
                product_id=int(row["product_id"]),
                product_name=row.get("product_name", product.name),
                category=row.get("category", product.category.name if product.category else None),
                units_sold=int(row["units_sold"]),
                selling_price=float(row["selling_price"]),
                promotion=promotion,
                discount=discount,
                holiday=holiday,
                store_location=row.get("store_location"),
                stock_available=product.current_stock,
            )
            db.add(db_sale)
            created += 1
        except Exception as e:
            errors.append(f"Row {idx + 1}: {str(e)}")

    upload_record.records_count = created
    upload_record.status = "completed" if not errors else "completed_with_errors"
    upload_record.error_message = "; ".join(errors[:10]) if errors else None

    db.commit()
    return {"created": created, "errors": errors, "upload_id": upload_record.id}


@router.get("/trends")
def get_sales_trends(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    sales = db.query(Sale).filter(Sale.date >= cutoff_date).order_by(Sale.date).all()

    daily_sales = {}
    for sale in sales:
        day_str = sale.date.strftime("%Y-%m-%d")
        if day_str not in daily_sales:
            daily_sales[day_str] = {"date": day_str, "total_units": 0, "total_revenue": 0.0, "num_transactions": 0}
        daily_sales[day_str]["total_units"] += sale.units_sold
        daily_sales[day_str]["total_revenue"] += sale.selling_price * sale.units_sold
        daily_sales[day_str]["num_transactions"] += 1

    return list(daily_sales.values())
