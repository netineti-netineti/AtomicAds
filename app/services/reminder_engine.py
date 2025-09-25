# app/services/reminder_engine.py
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

from app.services.visibilty import VisibilityResolver
from app.services.delivery.inapp import InAppStrategy
from app.db import SessionLocal
from app.model import Alert, NotificationDelivery, UserAlertPreference
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class ReminderEngine:
    """
    ReminderEngine is responsible for one "cycle" of reminder delivery.
    - Finds active alerts with reminders enabled and within start/expiry window.
    - Resolves recipients via VisibilityResolver.
    - Skips users who snoozed that alert for *today* (snooze stored as date).
    - Sends reminders only if no previous send exists within the reminder frequency window (idempotent).
    - Uses pluggable delivery strategies (default: in-app).
    """

    def __init__(self, db_session_factory=SessionLocal, strategies: Optional[Dict[str, object]] = None):
        """
        :param db_session_factory: callable returning DB Session (SessionLocal)
        :param strategies: optional mapping like {"inapp": InAppStrategy(...), "email": EmailStrategy(...)}
        """
        self.db_session_factory = db_session_factory
        self._strategies_override = strategies or {}

    def _make_strategies(self, db: Session) -> Dict[str, object]:
        """
        Build strategies using the current DB session if not provided via override.
        This ensures strategies that need DB get the correct session.
        """
        if self._strategies_override:
            return self._strategies_override
        return {"inapp": InAppStrategy(db)}

    def run_cycle(self) -> dict:
        """
        Run one reminder cycle. Meant to be called by a scheduler or the trigger endpoint.
        Returns a dict with simple statistics for testing / logs.
        """
        db = self.db_session_factory()
        sent_count = 0
        skipped_snoozed = 0
        skipped_recent = 0
        skipped_expired = 0
        try:
            now = datetime.utcnow()
            # Query candidate alerts: active, reminders enabled, started.
            alerts: List[Alert] = (
                db.query(Alert)
                .filter(Alert.status == "active", Alert.reminders_enabled == True, Alert.start_at <= now)
                .all()
            )

            strategies = self._make_strategies(db)

            for alert in alerts:
                # Skip expired alerts
                if alert.expires_at and alert.expires_at < now:
                    skipped_expired += 1
                    continue

                # Resolve recipients (list[User])
                recipients = VisibilityResolver.resolve(alert, db)
                for user in recipients:
                    # Check snooze: if snoozed_until == today, skip
                    pref: UserAlertPreference = (
                        db.query(UserAlertPreference)
                        .filter_by(user_id=user.id, alert_id=alert.id)
                        .first()
                    )
                    if pref and pref.snoozed_until == date.today():
                        skipped_snoozed += 1
                        continue

                    # Check last delivery time to avoid spamming: need to be older than freq
                    last: NotificationDelivery = (
                        db.query(NotificationDelivery)
                        .filter_by(alert_id=alert.id, user_id=user.id)
                        .order_by(NotificationDelivery.sent_at.desc())
                        .first()
                    )

                    freq_minutes = alert.reminder_frequency_minutes or 120
                    freq_delta = timedelta(minutes=freq_minutes)

                    if last and (last.sent_at + freq_delta) > now:
                        skipped_recent += 1
                        continue

                    # Send on each configured channel (strategy must exist)
                    for channel in (alert.delivery_types or []):
                        strat = strategies.get(channel)
                        if not strat:
                            logger.warning("No strategy for channel '%s', skipping", channel)
                            continue
                        try:
                            strat.send(alert, user)
                            sent_count += 1
                        except Exception as ex:
                            logger.exception("Failed to send alert %s to user %s via %s: %s", alert.id, user.id, channel, ex)

            return {
                "now": now.isoformat(),
                "alerts_checked": len(alerts),
                "sent_count": sent_count,
                "skipped_snoozed": skipped_snoozed,
                "skipped_recent": skipped_recent,
                "skipped_expired": skipped_expired,
            }
        finally:
            db.close()
