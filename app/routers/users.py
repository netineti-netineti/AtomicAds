# app/routers/user.py
from fastapi import APIRouter, HTTPException
from app.db import SessionLocal
from app.model import User, Alert, NotificationDelivery, UserAlertPreference
from app.services.preference_service import PreferenceService
from datetime import date

router = APIRouter()


@router.get("/{user_id}/alerts")
def get_user_alerts(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(404, "user not found")
        # compute active alerts for user
        alerts = db.query(Alert).filter(Alert.status == "active").all()
        user_alerts = []
        for a in alerts:
            vis = a.visibility or {}
            send = False
            if vis.get("org"):
                send = True
            if user.id in (vis.get("users") or []):
                send = True
            if user.team_id and user.team_id in (vis.get("teams") or []):
                send = True
            if not send:
                continue
            pref = db.query(UserAlertPreference).filter_by(user_id=user.id, alert_id=a.id).first()
            snoozed = pref.snoozed_until == date.today() if pref and pref.snoozed_until else False
            user_alerts.append({
                "id": a.id,
                "title": a.title,
                "body": a.body,
                "severity": a.severity,
                "snoozed": snoozed,
                "read": pref.read if pref else False
            })
        return {"alerts": user_alerts}
    finally:
        db.close()


@router.post("/{user_id}/alerts/{alert_id}/snooze")
def snooze(user_id: int, alert_id: int):
    svc = PreferenceService()
    pref = svc.snooze_for_today(user_id, alert_id)
    return {"detail": "snoozed", "snoozed_until": pref.snoozed_until}


@router.post("/{user_id}/alerts/{alert_id}/read")
def mark_read(user_id: int, alert_id: int):
    svc = PreferenceService()
    pref = svc.mark_read(user_id, alert_id)
    return {"detail": "marked read"}


@router.post("/{user_id}/alerts/{alert_id}/unread")
def mark_unread(user_id: int, alert_id: int):
    svc = PreferenceService()
    pref = svc.mark_unread(user_id, alert_id)
    return {"detail": "marked unread"}


@router.get("/{user_id}/alerts/snooze_history")
def snooze_history(user_id: int):
    db = SessionLocal()
    try:
        prefs = db.query(UserAlertPreference).filter_by(user_id=user_id).all()
        return {"history": [{"alert_id": p.alert_id, "snoozed_until": p.snoozed_until, "read": p.read} for p in prefs]}
    finally:
        db.close()
