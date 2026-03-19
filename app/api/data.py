from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Customer, Invoice, Payment
from app.schemas.schemas import CustomerResponse, InvoiceResponse, PaymentResponse

router = APIRouter(prefix="/data", tags=["Data"])


@router.get("/customers", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(customer_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Invoice)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    return query.all()


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/payments", response_model=list[PaymentResponse])
def list_payments(invoice_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Payment)
    if invoice_id:
        query = query.filter(Payment.invoice_id == invoice_id)
    return query.all()
