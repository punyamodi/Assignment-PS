"""
PaySaathi Integration Service — Main FastAPI Application.

Integrates with an external accounting system, stores data locally,
and exposes financial insight APIs.
"""
import logging

from fastapi import FastAPI

from app.database import init_db
from app.api.sync import router as sync_router
from app.api.insights import router as insights_router
from app.api.data import router as data_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="PaySaathi Integration Service",
    description=(
        "Integrates with an external accounting system to fetch customers, "
        "invoices, and payments. Provides financial insight APIs for outstanding "
        "balances, overdue invoices, credit summaries, and aging reports."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    """Initialize the database on application startup."""
    init_db()


app.include_router(sync_router)
app.include_router(insights_router)
app.include_router(data_router)


@app.get("/", tags=["System"])
def root():
    return {
        "service": "PaySaathi Integration Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "sync": "POST /sync/ — Trigger data sync from external system",
            "insights": {
                "outstanding_balances": "GET /insights/outstanding-balances",
                "overdue_invoices": "GET /insights/overdue-invoices",
                "customer_credit": "GET /insights/customer/{id}/credit-summary",
                "aging_report": "GET /insights/aging-report",
            },
            "data": {
                "customers": "GET /data/customers",
                "invoices": "GET /data/invoices",
                "payments": "GET /data/payments",
            },
        },
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
