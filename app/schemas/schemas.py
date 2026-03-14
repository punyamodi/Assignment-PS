"""
Pydantic schemas for API request/response models.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Customer Schemas
# ---------------------------------------------------------------------------

class CustomerBase(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(CustomerBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Invoice Schemas
# ---------------------------------------------------------------------------

class InvoiceBase(BaseModel):
    id: str
    customer_id: str
    invoice_number: Optional[str] = None
    amount: float
    due_date: date
    status: str
    issued_date: Optional[date] = None


class InvoiceResponse(InvoiceBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Payment Schemas
# ---------------------------------------------------------------------------

class PaymentBase(BaseModel):
    id: str
    invoice_id: str
    amount: float
    payment_date: date
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None


class PaymentResponse(PaymentBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Insight Schemas
# ---------------------------------------------------------------------------

class OutstandingBalance(BaseModel):
    customer_id: str
    customer_name: str
    total_invoiced: float
    total_paid: float
    outstanding_balance: float
    overdue_amount: float
    invoice_count: int


class OverdueInvoice(BaseModel):
    invoice_id: str
    invoice_number: Optional[str]
    customer_id: str
    customer_name: str
    amount: float
    paid_amount: float
    outstanding: float
    due_date: date
    days_overdue: int


class CustomerCreditSummary(BaseModel):
    customer_id: str
    customer_name: str
    email: Optional[str]
    total_invoices: int
    total_invoiced_amount: float
    total_paid_amount: float
    outstanding_balance: float
    overdue_invoices: int
    overdue_amount: float
    avg_days_to_pay: Optional[float]
    payment_history: List[PaymentResponse]
    risk_rating: str  # low | medium | high


class AgingBucket(BaseModel):
    bucket: str  # "0-30 days", "31-60 days", "61-90 days", "90+ days"
    total_outstanding: float
    invoice_count: int
    customers: List[str]


class AgingReport(BaseModel):
    generated_at: datetime
    total_receivables: float
    buckets: List[AgingBucket]


class SyncResult(BaseModel):
    entity: str
    records_synced: int
    status: str
    message: Optional[str] = None
