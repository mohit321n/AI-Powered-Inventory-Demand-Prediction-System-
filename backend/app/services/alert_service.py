from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Product, Alert, AlertType, AlertSeverity


def generate_alerts(db: Session) -> List[Alert]:
    alerts = []
    alerts.extend(check_low_stock_alerts(db))
    products = db.query(Product).all()
    for product in products:
        alerts.extend(check_overstock(db, product.id))
    return alerts


def check_low_stock_alerts(db: Session) -> List[Alert]:
    products = db.query(Product).filter(
        Product.current_stock <= Product.minimum_stock
    ).all()

    alerts = []
    for product in products:
        existing = db.query(Alert).filter(
            Alert.product_id == product.id,
            Alert.alert_type == AlertType.LOW_STOCK,
            Alert.is_read == False
        ).first()

        if not existing:
            alert = Alert(
                product_id=product.id,
                alert_type=AlertType.LOW_STOCK,
                severity=AlertSeverity.HIGH if product.current_stock == 0 else AlertSeverity.MEDIUM,
                message=f"Stock is low: {product.current_stock} remaining (minimum: {product.minimum_stock})"
            )
            db.add(alert)
            alerts.append(alert)

    db.commit()
    return alerts


def check_stockout_risk(db: Session, product_id: int, forecast: dict) -> Optional[Alert]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    forecasted_demand = forecast.get("forecasted_quantity", 0)
    if forecasted_demand > product.current_stock:
        alert = Alert(
            product_id=product_id,
            alert_type=AlertType.STOCKOUT_RISK,
            severity=AlertSeverity.HIGH,
            message=f"Stockout risk: forecasted demand ({forecasted_demand}) exceeds current stock ({product.current_stock})"
        )
        db.add(alert)
        db.commit()
        return alert
    return None


def check_overstock(db: Session, product_id: int) -> List[Alert]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return []

    alerts = []
    if product.maximum_stock and product.current_stock > product.maximum_stock:
        existing = db.query(Alert).filter(
            Alert.product_id == product_id,
            Alert.alert_type == AlertType.OVERSTOCK,
            Alert.is_read == False
        ).first()

        if not existing:
            alert = Alert(
                product_id=product_id,
                alert_type=AlertType.OVERSTOCK,
                severity=AlertSeverity.LOW,
                message=f"Overstock: {product.current_stock} exceeds maximum ({product.maximum_stock})"
            )
            db.add(alert)
            alerts.append(alert)
            db.commit()

    return alerts


def get_alerts(
    db: Session,
    product_id: Optional[int] = None,
    alert_type: Optional[AlertType] = None,
    severity: Optional[AlertSeverity] = None,
    is_read: Optional[bool] = None
) -> List[Alert]:
    query = db.query(Alert)
    if product_id:
        query = query.filter(Alert.product_id == product_id)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    return query.order_by(Alert.created_at.desc()).all()


def mark_alert_read(db: Session, alert_id: int) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert


def get_alert_summary(db: Session) -> dict:
    total = db.query(Alert).count()
    unread = db.query(Alert).filter(Alert.is_read == False).count()
    high = db.query(Alert).filter(
        Alert.severity == AlertSeverity.HIGH,
        Alert.is_read == False
    ).count()
    medium = db.query(Alert).filter(
        Alert.severity == AlertSeverity.MEDIUM,
        Alert.is_read == False
    ).count()
    low = db.query(Alert).filter(
        Alert.severity == AlertSeverity.LOW,
        Alert.is_read == False
    ).count()

    return {
        "total_alerts": total,
        "unread_alerts": unread,
        "high_severity": high,
        "medium_severity": medium,
        "low_severity": low
    }
