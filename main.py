from fastapi import FastAPI
from app.db import init_db
from app.routers import admin, users


app = FastAPI(title="Alerting Platform MVP")


# Initialize DB (creates sqlite file and tables if not present)
init_db()


app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(users.router, prefix="/user", tags=["user"])



@app.get("/")
def root():
    return {"message":"Alerting Platform MVP - see /docs"}