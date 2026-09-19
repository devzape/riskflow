import pandas as pd
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.alert import Alert


def build_analytics_summary(db: Session) -> dict:
    transactions = db.query(Transaction).all()
    alerts = db.query(Alert).all()

    if not transactions:
        return {
            "total_transactions": 0,
            "total_amount": 0.0,
            "flagged_transactions": 0,
            "flagged_rate": 0.0,
            "daily_volume": [],
            "top_flagged_accounts": [],
            "alerts_by_severity": {},
        }

    tx_df = pd.DataFrame([
        {
            "id": t.id,
            "origin_account_id": t.origin_account_id,
            "amount": float(t.amount),
            "timestamp": t.timestamp,
            "status": t.status,
        }
        for t in transactions
    ])

    total_transactions = len(tx_df)
    total_amount = tx_df["amount"].sum()
    flagged_transactions = (tx_df["status"] == "flagged").sum()
    flagged_rate = round(flagged_transactions / total_transactions, 4) if total_transactions else 0.0

    # Volumen diario
    tx_df["date"] = tx_df["timestamp"].apply(lambda ts: ts.date().isoformat())
    daily = tx_df.groupby("date").agg(
        total_amount=("amount", "sum"),
        transaction_count=("id", "count"),
    ).reset_index()
    daily_volume = daily.to_dict(orient="records")

    # Top cuentas con más alertas
    top_flagged_accounts = []
    alerts_by_severity = {}

    if alerts:
        alert_df = pd.DataFrame([
            {
                "id": a.id,
                "transaction_id": a.transaction_id,
                "severity": a.severity,
            }
            for a in alerts
        ])

        merged = alert_df.merge(
            tx_df[["id", "origin_account_id"]],
            left_on="transaction_id",
            right_on="id",
            suffixes=("_alert", "_tx"),
        )

        top_accounts = (
            merged.groupby("origin_account_id")
            .size()
            .reset_index(name="alert_count")
            .sort_values("alert_count", ascending=False)
            .head(5)
        )
        top_flagged_accounts = [
            {"account_id": int(row["origin_account_id"]), "alert_count": int(row["alert_count"])}
            for _, row in top_accounts.iterrows()
        ]

        alerts_by_severity = alert_df["severity"].value_counts().to_dict()

    return {
        "total_transactions": total_transactions,
        "total_amount": round(float(total_amount), 2),
        "flagged_transactions": int(flagged_transactions),
        "flagged_rate": flagged_rate,
        "daily_volume": daily_volume,
        "top_flagged_accounts": top_flagged_accounts,
        "alerts_by_severity": alerts_by_severity,
    }