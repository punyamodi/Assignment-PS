
from datetime import date, timedelta

from app.models.models import Customer, Invoice, Payment
from app.services.insight_service import InsightService


def _seed_data(db):
    """Seed the test database with sample data."""
    today = date.today()

    # Customers
    c1 = Customer(id="C1", name="Alpha Corp", email="alpha@test.com")
    c2 = Customer(id="C2", name="Beta Ltd", email="beta@test.com")
    db.add_all([c1, c2])
    db.flush()

    # Invoices
    inv1 = Invoice(
        id="I1", customer_id="C1", invoice_number="INV-001",
        amount=100000, due_date=today - timedelta(days=45),
        status="overdue", issued_date=today - timedelta(days=75),
    )
    inv2 = Invoice(
        id="I2", customer_id="C1", invoice_number="INV-002",
        amount=50000, due_date=today - timedelta(days=5),
        status="paid", issued_date=today - timedelta(days=35),
    )
    inv3 = Invoice(
        id="I3", customer_id="C2", invoice_number="INV-003",
        amount=200000, due_date=today + timedelta(days=15),
        status="pending", issued_date=today - timedelta(days=10),
    )
    inv4 = Invoice(
        id="I4", customer_id="C2", invoice_number="INV-004",
        amount=80000, due_date=today - timedelta(days=70),
        status="overdue", issued_date=today - timedelta(days=100),
    )
    db.add_all([inv1, inv2, inv3, inv4])
    db.flush()

    # Payments
    pay1 = Payment(
        id="P1", invoice_id="I2", amount=50000,
        payment_date=today - timedelta(days=3), payment_method="bank_transfer",
    )
    pay2 = Payment(
        id="P2", invoice_id="I1", amount=30000,
        payment_date=today - timedelta(days=20), payment_method="upi",
    )
    pay3 = Payment(
        id="P3", invoice_id="I4", amount=20000,
        payment_date=today - timedelta(days=50), payment_method="cash",
    )
    db.add_all([pay1, pay2, pay3])
    db.commit()


class TestOutstandingBalances:
    def test_returns_all_customers(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        result = service.get_outstanding_balances()
        assert len(result) == 2

    def test_correct_outstanding_balance(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        result = service.get_outstanding_balances()
        balances = {r.customer_id: r for r in result}

        # C1: invoiced=150000, paid=80000 (50000+30000), outstanding=70000
        assert balances["C1"].total_invoiced == 150000
        assert balances["C1"].total_paid == 80000
        assert balances["C1"].outstanding_balance == 70000

        # C2: invoiced=280000, paid=20000, outstanding=260000
        assert balances["C2"].total_invoiced == 280000
        assert balances["C2"].total_paid == 20000
        assert balances["C2"].outstanding_balance == 260000

    def test_sorted_by_outstanding_desc(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        result = service.get_outstanding_balances()
        # C2 has higher outstanding (260000) than C1 (70000)
        assert result[0].customer_id == "C2"
        assert result[1].customer_id == "C1"


class TestOverdueInvoices:
    def test_returns_only_overdue_unpaid(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        result = service.get_overdue_invoices()
        ids = [r.invoice_id for r in result]
        # I1 (overdue, partially paid) and I4 (overdue, partially paid)
        assert "I1" in ids
        assert "I4" in ids
        # I2 is paid, I3 is not yet due
        assert "I2" not in ids
        assert "I3" not in ids

    def test_correct_outstanding_amounts(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        result = service.get_overdue_invoices()
        invoices = {r.invoice_id: r for r in result}

        assert invoices["I1"].outstanding == 70000  # 100000 - 30000
        assert invoices["I4"].outstanding == 60000  # 80000 - 20000

    def test_days_overdue_positive(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        result = service.get_overdue_invoices()
        for inv in result:
            assert inv.days_overdue > 0


class TestCustomerCreditSummary:
    def test_returns_none_for_unknown(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        assert service.get_customer_credit_summary("UNKNOWN") is None

    def test_correct_summary(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        summary = service.get_customer_credit_summary("C1")

        assert summary.customer_id == "C1"
        assert summary.total_invoices == 2
        assert summary.total_invoiced_amount == 150000
        assert summary.total_paid_amount == 80000
        assert summary.outstanding_balance == 70000

    def test_risk_rating(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)

        # C2 has overdue_amount = 60000 out of 280000 = 21.4% → medium
        summary_c2 = service.get_customer_credit_summary("C2")
        assert summary_c2.risk_rating == "medium"


class TestAgingReport:
    def test_report_has_four_buckets(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        report = service.get_aging_report()
        assert len(report.buckets) == 4

    def test_total_receivables_correct(self, db_session):
        _seed_data(db_session)
        service = InsightService(db_session)
        report = service.get_aging_report()
        # Outstanding: I1=70000, I3=200000, I4=60000 = 330000
        assert report.total_receivables == 330000
