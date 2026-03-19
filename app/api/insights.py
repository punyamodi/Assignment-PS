from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.insight_service import InsightService
from app.schemas.schemas import (
    OutstandingBalance,
    OverdueInvoice,
    CustomerCreditSummary,
    AgingReport,
)

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/outstanding-balances", response_model=list[OutstandingBalance])
def outstanding_balances(db: Session = Depends(get_db)):
    service = InsightService(db)
    return service.get_outstanding_balances()


@router.get("/overdue-invoices", response_model=list[OverdueInvoice])
def overdue_invoices(db: Session = Depends(get_db)):
    service = InsightService(db)
    return service.get_overdue_invoices()


@router.get("/customer/{customer_id}/credit-summary", response_model=CustomerCreditSummary)
def customer_credit_summary(customer_id: str, db: Session = Depends(get_db)):
    service = InsightService(db)
    result = service.get_customer_credit_summary(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return result


@router.get("/aging-report", response_model=AgingReport)
def aging_report(db: Session = Depends(get_db)):
    service = InsightService(db)
    return service.get_aging_report()
