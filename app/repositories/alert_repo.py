from app.db import SessionLocal
from app.model import Alert, User, NotificationDelivery, UserAlertPreference
from sqlalchemy.orm import Session
from typing import List


class AlertRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Alert:
        alert = Alert(**kwargs)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def update(self, alert: Alert, **kwargs):
        for k, v in kwargs.items():
            setattr(alert, k, v)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get(self, alert_id: int):
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def list_all(self, filters: dict = None):
        q = self.db.query(Alert)
        if filters:
            if "severity" in filters:
                q = q.filter(Alert.severity == filters["severity"])
            if "status" in filters:
                q = q.filter(Alert.status == filters["status"])
        return q.all()

    def deliveries_for(self, alert_id: int):
        return self.db.query(NotificationDelivery).filter(NotificationDelivery.alert_id == alert_id).all()

    def get_or_create_pref(self, user_id: int, alert_id: int):
        pref = self.db.query(UserAlertPreference).filter_by(user_id=user_id, alert_id=alert_id).first()
        if not pref:
            pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
            self.db.add(pref)
            self.db.commit()
            self.db.refresh(pref)
        return pref