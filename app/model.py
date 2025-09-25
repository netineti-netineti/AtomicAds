from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, Date
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime


Base = declarative_base()


class Severity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="team")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="users")
    is_admin = Column(Boolean, default=False)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    severity = Column(Enum(Severity), default=Severity.info)
    delivery_types = Column(JSON, default=["inapp"]) # list
    start_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    reminders_enabled = Column(Boolean, default=True)
    reminder_frequency_minutes = Column(Integer, default=120)
    visibility = Column(JSON, default={"org": False, "teams": [], "users": []})
    status = Column(String, default="active")


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    sent_at = Column(DateTime, default=datetime.utcnow)
    channel = Column(String)
    delivered = Column(Boolean, default=True)
    read = Column(Boolean, default=False)


class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    snoozed_until = Column(Date, nullable=True)
    read = Column(Boolean, default=False)