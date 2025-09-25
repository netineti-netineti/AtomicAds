# app/services/preference_service.py
from app.db import SessionLocal
from app.model import UserAlertPreference
from datetime import date
from sqlalchemy.orm import Session
from typing import Optional


class PreferenceService:
    def __init__(self, db_session_factory=SessionLocal):
        self.db_session_factory = db_session_factory

    def snooze_for_today(self, user_id: int, alert_id: int) -> UserAlertPreference:
        db: Session = self.db_session_factory()
        try:
            pref = db.query(UserAlertPreference).filter_by(user_id=user_id, alert_id=alert_id).first()
            if not pref:
                pref = UserAlertPreference(user_id=user_id, alert_id=alert_id, snoozed_until=date.today())
                db.add(pref)
            else:
                pref.snoozed_until = date.today()
            db.commit()
            db.refresh(pref)
            return pref
        finally:
            db.close()

    def mark_read(self, user_id: int, alert_id: int) -> UserAlertPreference:
        db: Session = self.db_session_factory()
        try:
            pref = db.query(UserAlertPreference).filter_by(user_id=user_id, alert_id=alert_id).first()
            if not pref:
                pref = UserAlertPreference(user_id=user_id, alert_id=alert_id, read=True)
                db.add(pref)
            else:
                pref.read = True
            db.commit()
            db.refresh(pref)
            return pref
        finally:
            db.close()

    def mark_unread(self, user_id: int, alert_id: int) -> Optional[UserAlertPreference]:
        db: Session = self.db_session_factory()
        try:
            pref = db.query(UserAlertPreference).filter_by(user_id=user_id, alert_id=alert_id).first()
            if pref:
                pref.read = False
                db.commit()
                db.refresh(pref)
            return pref
        finally:
            db.close()
