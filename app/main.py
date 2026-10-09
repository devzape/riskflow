from fastapi import FastAPI
from app.routers import auth, accounts, transactions, risk_rules, alerts, analytics

app = FastAPI(title="RiskFlow")

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(risk_rules.router)
app.include_router(alerts.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "RiskFlow API running"}