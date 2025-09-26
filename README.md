# Alert Management System

A backend system for managing alerts and notifications, built with extensibility and maintainability in mind. It supports multiple delivery channels, user subscriptions, and alert state management (read, unread, snoozed).

---

## Features

- **Admin APIs**: Create, update, and list alerts.  
- **User APIs**: Fetch alerts, mark read/unread, snooze alerts.  
- **Analytics**: Aggregated alert data for insights.  
- **Design Principles**:  
  - DRY (Don’t Repeat Yourself)  
  - SRP (Single Responsibility Principle)  
  - Extensible via Strategy, Observer, and State Patterns  
- **Seed Data**: Predefined users and teams for testing  
- **Pluggable Channels**: Add new delivery channels without affecting existing code  

---

## Tech Stack

- Python 3.10+  
- FastAPI  
- SQLAlchemy (SQLite by default, configurable for other databases)  
- JWT-based authentication (demo)  

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/netineti-netineti/AtomicAds.git
cd alert-management-system
```

### 2. Setup virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize database and seed data
```bash
python scripts/init_db.py
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

Server will start at: `http://127.0.0.1:8000`

---

## API Endpoints

### Admin
- `POST /admin/alerts` — Create Alert  
- `PUT /admin/alerts/{id}` — Update Alert  
- `GET /admin/alerts` — List Alerts  

### User
- `GET /user/alerts` — Fetch Alerts  
- `PATCH /user/alerts/{id}/read` — Mark as Read  
- `PATCH /user/alerts/{id}/unread` — Mark as Unread  
- `PATCH /user/alerts/{id}/snooze` — Snooze Alert  

### Analytics
- `GET /analytics/alerts` — Get aggregated alert data  

---

## Seed Data

The database is seeded with sample users and teams for quick testing.  
Example:  
- Users: Alice, Bob  
- Teams: Engineering, Marketing  

---

```

---

---

## Roadmap

- Add push notifications  
- Role-based access control (RBAC)  
- WebSocket support for live updates  

---

## License

MIT License © 2025
