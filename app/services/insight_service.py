"""
Insight service — computes financial insights from locally stored data.
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Customer, Invoice, Payment
from app.schemas.schemas import (
    OutstandingBalance,
    OverdueInvoice,
    CustomerCreditSummary,
    AgingBucket,
    AgingReport,
    PaymentResponse,
)


class InsightService:
    """Computes credit insights from the local data store."""

    def __init__(self, db: Session):
        self.db = db

    def get_outstanding_balances(self) -> list[OutstandingBalance]:
        """Per-customer outstanding balance = total invoiced - total paid."""
        customers = self.db.query(Customer).all()
        results = []

        for customer in customers:
            invoices = self.db.query(Invoice).filter(Invoice.customer_id == customer.id).all()
            total_invoiced = sum(inv.amount for inv in invoices)
            total_paid = 0.0
            overdue_amount = 0.0
            today = date.today()

            for inv in invoices:
                paid = sum(p.amount for p in inv.payments)
                total_paid += paid
                if inv.due_date < today and inv.status != "paid":
                    overdue_amount += (inv.amount - paid)

            outstanding = total_invoiced - total_paid
            results.append(OutstandingBalance(
                customer_id=customer.id,
                customer_name=customer.name,
                total_invoiced=round(total_invoiced, 2),
                total_paid=round(total_paid, 2),
                outstanding_balance=round(outstanding, 2),
                overdue_amount=round(overdue_amount, 2),
                invoice_count=len(invoices),
            ))

        # Sort by outstanding balance descending
        results.sort(key=lambda x: x.outstanding_balance, reverse=True)
        return results

    def get_overdue_invoices(self) -> list[OverdueInvoice]:
        """All invoices past due date that are not fully paid."""
        today = date.today()
        invoices = (
            self.db.query(Invoice)
            .filter(Invoice.due_date < today, Invoice.status != "paid")
            .all()
        )
        results = []

        for inv in invoices:
            paid_amount = sum(p.amount for p in inv.payments)
            outstanding = inv.amount - paid_amount
            if outstanding <= 0:
                continue

            customer = self.db.query(Customer).filter(Customer.id == inv.customer_id).first()
            days_overdue = (today - inv.due_date).days

            results.append(OverdueInvoice(
                invoice_id=inv.id,
                invoice_number=inv.invoice_number,
                customer_id=inv.customer_id,
                customer_name=customer.name if customer else "Unknown",
                amount=inv.amount,
                paid_amount=round(paid_amount, 2),
                outstanding=round(outstanding, 2),
                due_date=inv.due_date,
                days_overdue=days_overdue,
            ))

        # Sort by days overdue descending
        results.sort(key=lambda x: x.days_overdue, reverse=True)
        return results

    def get_customer_credit_summary(self, customer_id: str) -> Optional[CustomerCreditSummary]:
        """Full credit profile for a single customer."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None

        invoices = self.db.query(Invoice).filter(Invoice.customer_id == customer_id).all()
        today = date.today()

        total_invoiced = 0.0
        total_paid = 0.0
        overdue_count = 0
        overdue_amount = 0.0
        all_payments = []
        days_to_pay_list = []

        for inv in invoices:
            total_invoiced += inv.amount
            inv_paid = 0.0

            for p in inv.payments:
                inv_paid += p.amount
                all_payments.append(PaymentResponse(
                    id=p.id,
                    invoice_id=p.invoice_id,
                    amount=p.amount,
                    payment_date=p.payment_date,
                    payment_method=p.payment_method,
                    reference_number=p.reference_number,
                    created_at=p.created_at,
                ))
                # Calculate days to pay from issued date
                if inv.issued_date:
                    days = (p.payment_date - inv.issued_date).days
                    if days >= 0:
                        days_to_pay_list.append(days)

            total_paid += inv_paid

            if inv.due_date < today and inv.status != "paid":
                remaining = inv.amount - inv_paid
                if remaining > 0:
                    overdue_count += 1
                    overdue_amount += remaining

        outstanding = total_invoiced - total_paid
        avg_days = round(sum(days_to_pay_list) / len(days_to_pay_list), 1) if days_to_pay_list else None

        # Risk rating based on overdue ratio
        if total_invoiced == 0:
            risk = "low"
        else:
            overdue_ratio = overdue_amount / total_invoiced
            if overdue_ratio > 0.5:
                risk = "high"
            elif overdue_ratio > 0.2:
                risk = "medium"
            else:
                risk = "low"

        return CustomerCreditSummary(
            customer_id=customer.id,
            customer_name=customer.name,
            email=customer.email,
            total_invoices=len(invoices),
            total_invoiced_amount=round(total_invoiced, 2),
            total_paid_amount=round(total_paid, 2),
            outstanding_balance=round(outstanding, 2),
            overdue_invoices=overdue_count,
            overdue_amount=round(overdue_amount, 2),
            avg_days_to_pay=avg_days,
            payment_history=sorted(all_payments, key=lambda p: p.payment_date, reverse=True),
            risk_rating=risk,
        )

    def get_aging_report(self) -> AgingReport:
        """Receivables aging buckets: 0-30, 31-60, 61-90, 90+ days."""
        today = date.today()
        invoices = (
            self.db.query(Invoice)
            .filter(Invoice.status != "paid")
            .all()
        )

        buckets = {
            "0-30 days": {"total": 0.0, "count": 0, "customers": set()},
            "31-60 days": {"total": 0.0, "count": 0, "customers": set()},
            "61-90 days": {"total": 0.0, "count": 0, "customers": set()},
            "90+ days": {"total": 0.0, "count": 0, "customers": set()},
        }

        total_receivables = 0.0

        for inv in invoices:
            paid = sum(p.amount for p in inv.payments)
            outstanding = inv.amount - paid
            if outstanding <= 0:
                continue

            total_receivables += outstanding
            days_outstanding = (today - inv.due_date).days if inv.due_date <= today else 0

            if days_outstanding <= 0:
                # Not yet due — put in 0-30 bucket
                bucket_key = "0-30 days"
            elif days_outstanding <= 30:
                bucket_key = "0-30 days"
            elif days_outstanding <= 60:
                bucket_key = "31-60 days"
            elif days_outstanding <= 90:
                bucket_key = "61-90 days"
            else:
                bucket_key = "90+ days"

            buckets[bucket_key]["total"] += outstanding
            buckets[bucket_key]["count"] += 1
            buckets[bucket_key]["customers"].add(inv.customer_id)

        bucket_list = [
            AgingBucket(
                bucket=key,
                total_outstanding=round(data["total"], 2),
                invoice_count=data["count"],
                customers=sorted(data["customers"]),
            )
            for key, data in buckets.items()
        ]

        return AgingReport(
            generated_at=datetime.utcnow(),
            total_receivables=round(total_receivables, 2),
            buckets=bucket_list,
        )
