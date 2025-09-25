from app.model import User, Team, Alert
from sqlalchemy.orm import Session
from typing import List


class VisibilityResolver:
    @staticmethod
    def resolve(alert: Alert, db: Session) -> List[User]:
        vis = alert.visibility or {}
        if vis.get("org"):
            return db.query(User).all()
        user_ids = set(vis.get("users", []) or [])
        team_ids = vis.get("teams", []) or []
        if team_ids:
            users_in_teams = db.query(User).filter(User.team_id.in_(team_ids)).all()
            for u in users_in_teams:
                user_ids.add(u.id)
        # fetch users by ids (avoid duplicates)
        if user_ids:
            return db.query(User).filter(User.id.in_(list(user_ids))).all()
        return []