# Alerting Platform MVP


**A lightweight alerting & notification backend (FastAPI + SQLite)**


## Features
- Admin: create/update/archive alerts; list & filter alerts; trigger reminders (demo)
- User: fetch alerts (with read/unread/snooze), mark read/unread, snooze for current day
- Reminder engine: `trigger_reminders` endpoint runs reminder logic (simulates 2-hour reminders)
- In-App delivery strategy (pluggable)
- Seed data for teams/users
- Analytics endpoint for basic aggregated metrics


## Quickstart
1. Clone the repo
2. Create and activate a virtualenv


```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt