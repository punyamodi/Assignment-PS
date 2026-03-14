"""
Sync service — fetches data from the external accounting API and upserts into local DB.
"""
import logging
from datetime import datetime, date

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Customer, Invoice, Payment, SyncLog

logger = logging.getLogger(__name__)


class SyncService:
    """Handles data synchronization from external accounting system."""

    def __init__(self, db: Session):
        self.db = db
        self.base_url = settings.EXTERNAL_API_BASE_URL
        self.timeout = settings.SYNC_TIMEOUT_SECONDS

    async def sync_all(self) -> list[dict]:
        """Run full sync for customers, invoices, and payments (in order)."""
        results = []
        for entity, sync_fn in [
            ("customers", self._sync_customers),
            ("invoices", self._sync_invoices),
            ("payments", self._sync_payments),
        ]:
            log = SyncLog(entity_type=entity, status="started", started_at=datetime.utcnow())
            self.db.add(log)
            self.db.commit()

            try:
                count = await sync_fn()
                log.status = "completed"
                log.records_synced = count
                log.completed_at = datetime.utcnow()
                results.append({"entity": entity, "records_synced": count, "status": "completed"})
            except Exception as e:
                log.status = "failed"
                log.error_message = str(e)
                log.completed_at = datetime.utcnow()
                results.append({"entity": entity, "records_synced": 0, "status": "failed", "message": str(e)})
                logger.error(f"Sync failed for {entity}: {e}")
            finally:
                self.db.commit()

        return results

    async def _fetch_json(self, endpoint: str) -> dict:
        """Fetch JSON from the external API with timeout and error handling."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()

    async def _sync_customers(self) -> int:
        data = await self._fetch_json("/customers")
        customers = data.get("data", [])
        count = 0

        for c in customers:
            existing = self.db.query(Customer).filter(Customer.id == c["id"]).first()
            if existing:
                existing.name = c["name"]
                existing.email = c.get("email")
                existing.phone = c.get("phone")
                existing.address = c.get("address")
                existing.updated_at = datetime.utcnow()
            else:
                self.db.add(Customer(
                    id=c["id"],
                    name=c["name"],
                    email=c.get("email"),
                    phone=c.get("phone"),
                    address=c.get("address"),
                ))
            count += 1

        self.db.commit()
        return count

    async def _sync_invoices(self) -> int:
        data = await self._fetch_json("/invoices")
        invoices = data.get("data", [])
        count = 0

        for inv in invoices:
            existing = self.db.query(Invoice).filter(Invoice.id == inv["id"]).first()
            due_date = date.fromisoformat(inv["due_date"])
            issued_date = date.fromisoformat(inv["issued_date"]) if inv.get("issued_date") else None

            if existing:
                existing.customer_id = inv["customer_id"]
                existing.invoice_number = inv.get("invoice_number")
                existing.amount = inv["amount"]
                existing.due_date = due_date
                existing.status = inv["status"]
                existing.issued_date = issued_date
                existing.updated_at = datetime.utcnow()
            else:
                self.db.add(Invoice(
                    id=inv["id"],
                    customer_id=inv["customer_id"],
                    invoice_number=inv.get("invoice_number"),
                    amount=inv["amount"],
                    due_date=due_date,
                    status=inv["status"],
                    issued_date=issued_date,
                ))
            count += 1

        self.db.commit()
        return count

    async def _sync_payments(self) -> int:
        data = await self._fetch_json("/payments")
        payments = data.get("data", [])
        count = 0

        for p in payments:
            existing = self.db.query(Payment).filter(Payment.id == p["id"]).first()
            payment_date = date.fromisoformat(p["payment_date"])

            if existing:
                existing.invoice_id = p["invoice_id"]
                existing.amount = p["amount"]
                existing.payment_date = payment_date
                existing.payment_method = p.get("payment_method")
                existing.reference_number = p.get("reference_number")
            else:
                self.db.add(Payment(
                    id=p["id"],
                    invoice_id=p["invoice_id"],
                    amount=p["amount"],
                    payment_date=payment_date,
                    payment_method=p.get("payment_method"),
                    reference_number=p.get("reference_number"),
                ))
            count += 1

        self.db.commit()
        return count
