# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.db import SessionLocal
from app.repositories.alert_repo import AlertRepo
from app.schemas import AlertCreate, AlertUpdate
from app.services.reminder_engine import ReminderEngine
from app.model import User, Alert, NotificationDelivery, UserAlertPreference
from sqlalchemy import func
from typing import Optional

router = APIRouter()


# Simple admin guard (demo): pass ?is_admin=true to simulate admin
def require_admin(is_admin: Optional[bool] = Query(False)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return True


@router.post("/alerts")
def create_alert(payload: AlertCreate, is_admin: bool = Depends(require_admin)):
    db = SessionLocal()
    try:
        repo = AlertRepo(db)
        alert = repo.create(**payload.dict(exclude_unset=True))
        return {"alert_id": alert.id}
    finally:
        db.close()


@router.put("/alerts/{alert_id}")
def update_alert(alert_id: int, payload: AlertUpdate, is_admin: bool = Depends(require_admin)):
    db = SessionLocal()
    try:
        repo = AlertRepo(db)
        a = repo.get(alert_id)
        if not a:
            raise HTTPException(404, "Not found")
        updated = repo.update(a, **payload.dict(exclude_unset=True))
        return {"alert_id": updated.id}
    finally:
        db.close()


@router.get("/alerts")
def list_alerts(is_admin: bool = Depends(require_admin), severity: Optional[str] = None, status: Optional[str] = None):
    db = SessionLocal()
    try:
        repo = AlertRepo(db)
        filters = {}
        if severity:
            filters["severity"] = severity
        if status:
            filters["status"] = status
        alerts = repo.list_all(filters)
        return {"alerts": [{"id": a.id, "title": a.title, "severity": a.severity, "status": a.status} for a in alerts]}
    finally:
        db.close()


@router.post("/trigger_reminders")
def trigger_reminders(is_admin: bool = Depends(require_admin)):
    engine = ReminderEngine()
    stats = engine.run_cycle()
    return {"detail": "reminder cycle executed", "stats": stats}


@router.get("/analytics")
def analytics(is_admin: bool = Depends(require_admin)):
    db = SessionLocal()
    try:
        total_alerts = db.query(func.count(Alert.id)).scalar() or 0
        deliveries_total = db.query(func.count(NotificationDelivery.id)).scalar() or 0
        reads_total = db.query(func.count(NotificationDelivery.id)).filter(NotificationDelivery.read == True).scalar() or 0
        snoozes = db.query(func.count(UserAlertPreference.id)).filter(UserAlertPreference.snoozed_until != None).scalar() or 0

        by_severity = db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
        severity_breakdown = {s.value if hasattr(s, "value") else s: c for s, c in by_severity}

        return {
            "total_alerts": total_alerts,
            "deliveries_total": deliveries_total,
            "reads_total": reads_total,
            "snoozes_total": snoozes,
            "by_severity": severity_breakdown,
        }
    finally:
        db.close()
