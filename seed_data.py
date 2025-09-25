# seed_data.py
from app.db import init_db, SessionLocal
from app.model import Team, User, Alert
from datetime import datetime, timedelta

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        # if teams exist, don't duplicate
        if db.query(Team).count() > 0:
            print("DB already seeded (teams exist).")
        else:
            # create teams
            eng = Team(name="Engineering")
            mkt = Team(name="Marketing")
            db.add_all([eng, mkt])
            db.commit()
            db.refresh(eng); db.refresh(mkt)

            # create users
            alice = User(name="Alice", team_id=eng.id, is_admin=True)
            bob = User(name="Bob", team_id=eng.id)
            carol = User(name="Carol", team_id=mkt.id)
            dave = User(name="Dave", team_id=None)
            db.add_all([alice, bob, carol, dave])
            db.commit()

            # create alerts
            now = datetime.utcnow()
            a1 = Alert(
                title="Org maintenance",
                body="We will have a maintenance window.",
                severity="warning",
                delivery_types=["inapp"],
                start_at=now - timedelta(hours=1),
                expires_at=now + timedelta(days=1),
                visibility={"org": True, "teams": [], "users": []},
            )
            a2 = Alert(
                title="Eng-only update",
                body="Engineering doc updated.",
                severity="info",
                delivery_types=["inapp"],
                start_at=now - timedelta(hours=1),
                visibility={"org": False, "teams": [eng.id], "users": []},
            )
            a3 = Alert(
                title="Personal note",
                body="Hey Bob — please review.",
                severity="info",
                delivery_types=["inapp"],
                start_at=now - timedelta(hours=1),
                visibility={"org": False, "teams": [], "users": [2]},
            )
            db.add_all([a1, a2, a3])
            db.commit()
            print("Seeded DB with teams, users, and alerts. Users: Alice(id=1,is_admin), Bob(id=2), Carol(id=3), Dave(id=4)")
    finally:
        db.close()