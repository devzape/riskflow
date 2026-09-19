from fastapi import FastAPI
from app.database import engine, Base
from app.models import user, account, transaction, risk_rule, alert
from app.routers import auth

app = FastAPI(title="RiskFlow")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "RiskFlow API running"}

Base.metadata.create_all(bind=engine)

from app.routers import auth, accounts, transactions

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)