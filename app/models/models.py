"""
SQLAlchemy models for the local accounting data store.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Float, Date, DateTime, ForeignKey, Integer, Text, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, doc="External customer ID")
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name})>"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, doc="External invoice ID")
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_number = Column(String, nullable=True, unique=True)
    amount = Column(Float, nullable=False, doc="Total invoice amount")
    due_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="pending", doc="pending | paid | partially_paid | overdue")
    issued_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_invoices_due_date", "due_date"),
        Index("ix_invoices_status", "status"),
    )

    def __repr__(self):
        return f"<Invoice(id={self.id}, amount={self.amount}, status={self.status})>"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, doc="External payment ID")
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False, doc="Payment amount")
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String, nullable=True, doc="cash | bank_transfer | upi | card")
    reference_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount})>"


class SyncLog(Base):
    """Tracks sync operations for auditability and idempotency."""
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String, nullable=False, doc="customers | invoices | payments")
    status = Column(String, nullable=False, doc="started | completed | failed")
    records_synced = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
