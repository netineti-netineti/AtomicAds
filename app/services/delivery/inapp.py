from app.services.delivery.strategy import DeliveryStrategy
from app.db import SessionLocal
from app.model import NotificationDelivery
from datetime import datetime


class InAppStrategy(DeliveryStrategy):
    def __init__(self, db):
        self.db = db


def send(self, alert, user):
    nd = NotificationDelivery(alert_id=alert.id, user_id=user.id, sent_at=datetime.utcnow(), channel="inapp")
    self.db.add(nd)
    self.db.commit()
    # In a real app, you would publish to a websocket or push channel here
    return nd