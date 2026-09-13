from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_user
from app.models import Alert, Product, User

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    message: str
    severity: str
    product_id: Optional[int]
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


class AlertSummary(BaseModel):
    total: int
    unread: int
    critical: int
    high: int
    medium: int
    low: int


@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    is_read: Optional[bool] = None,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Alert)
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    if severity:
        query = query.filter(Alert.severity == severity)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/summary", response_model=AlertSummary)
def get_alert_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(Alert).count()
    unread = db.query(Alert).filter(Alert.is_read == False).count()
    critical = db.query(Alert).filter(Alert.severity == "critical", Alert.is_read == False).count()
    high = db.query(Alert).filter(Alert.severity == "high", Alert.is_read == False).count()
    medium = db.query(Alert).filter(Alert.severity == "medium", Alert.is_read == False).count()
    low = db.query(Alert).filter(Alert.severity == "low", Alert.is_read == False).count()
    return AlertSummary(
        total=total,
        unread=unread,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
    )


@router.get("/product/{product_id}", response_model=list[AlertResponse])
def get_product_alerts(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db.query(Alert).filter(Alert.product_id == product_id).order_by(Alert.created_at.desc()).all()
