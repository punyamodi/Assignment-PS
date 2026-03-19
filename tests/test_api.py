from datetime import date, timedelta

from app.models.models import Customer, Invoice, Payment


def _seed_via_db(db):
    """Seed data directly for API integration tests."""
    today = date.today()
    c = Customer(id="C1", name="Test Corp", email="test@test.com")
    db.add(c)
    db.flush()

    inv = Invoice(
        id="I1", customer_id="C1", invoice_number="INV-T001",
        amount=50000, due_date=today - timedelta(days=10),
        status="overdue", issued_date=today - timedelta(days=40),
    )
    db.add(inv)
    db.flush()

    pay = Payment(
        id="P1", invoice_id="I1", amount=10000,
        payment_date=today - timedelta(days=5), payment_method="upi",
    )
    db.add(pay)
    db.commit()


class TestHealthAndRoot:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["service"] == "PaySaathi Integration Service"

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestDataEndpoints:
    def test_list_customers_empty(self, client):
        r = client.get("/data/customers")
        assert r.status_code == 200
        assert r.json() == []

    def test_list_customers_with_data(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/data/customers")
        assert r.status_code == 200
        assert len(r.json()) == 1
        assert r.json()[0]["id"] == "C1"

    def test_get_customer_not_found(self, client):
        r = client.get("/data/customers/NONEXISTENT")
        assert r.status_code == 404

    def test_list_invoices(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/data/invoices")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_list_payments(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/data/payments")
        assert r.status_code == 200
        assert len(r.json()) == 1


class TestInsightEndpoints:
    def test_outstanding_balances(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/insights/outstanding-balances")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["outstanding_balance"] == 40000

    def test_overdue_invoices(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/insights/overdue-invoices")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["days_overdue"] >= 10

    def test_customer_credit_summary(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/insights/customer/C1/credit-summary")
        assert r.status_code == 200
        data = r.json()
        assert data["customer_id"] == "C1"
        assert data["outstanding_balance"] == 40000
        assert data["risk_rating"] == "high"  # 40000/50000 = 80%

    def test_customer_credit_summary_not_found(self, client):
        r = client.get("/insights/customer/NONEXISTENT/credit-summary")
        assert r.status_code == 404

    def test_aging_report(self, client, db_session):
        _seed_via_db(db_session)
        r = client.get("/insights/aging-report")
        assert r.status_code == 200
        data = r.json()
        assert data["total_receivables"] == 40000
        assert len(data["buckets"]) == 4
