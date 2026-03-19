from datetime import date, timedelta
from fastapi import FastAPI

app = FastAPI(title="Mock External Accounting System", version="1.0.0")

CUSTOMERS = [
    {
        "id": "CUST-001",
        "name": "Rajesh Kumar Enterprises",
        "email": "rajesh@rkenterprises.in",
        "phone": "+91-9876543210",
        "address": "45 MG Road, Bengaluru, Karnataka 560001",
    },
    {
        "id": "CUST-002",
        "name": "Priya Textiles Pvt Ltd",
        "email": "priya@priyatextiles.in",
        "phone": "+91-9123456780",
        "address": "12 Nehru Street, Chennai, Tamil Nadu 600002",
    },
    {
        "id": "CUST-003",
        "name": "Green Valley Organics",
        "email": "info@greenvalley.in",
        "phone": "+91-8899776655",
        "address": "78 Station Road, Pune, Maharashtra 411001",
    },
    {
        "id": "CUST-004",
        "name": "Sharma & Sons Hardware",
        "email": "contact@sharmasons.in",
        "phone": "+91-7766554433",
        "address": "23 Lajpat Nagar, New Delhi 110024",
    },
    {
        "id": "CUST-005",
        "name": "Coastal Fisheries Co-op",
        "email": "ops@coastalfisheries.in",
        "phone": "+91-6655443322",
        "address": "5 Beach Road, Kochi, Kerala 682001",
    },
]

today = date.today()

INVOICES = [
    # CUST-001: has overdue and paid invoices
    {
        "id": "INV-001",
        "customer_id": "CUST-001",
        "invoice_number": "INV-2025-001",
        "amount": 150000.00,
        "due_date": (today - timedelta(days=45)).isoformat(),
        "status": "overdue",
        "issued_date": (today - timedelta(days=75)).isoformat(),
    },
    {
        "id": "INV-002",
        "customer_id": "CUST-001",
        "invoice_number": "INV-2025-002",
        "amount": 75000.00,
        "due_date": (today - timedelta(days=10)).isoformat(),
        "status": "paid",
        "issued_date": (today - timedelta(days=40)).isoformat(),
    },
    {
        "id": "INV-003",
        "customer_id": "CUST-001",
        "invoice_number": "INV-2025-003",
        "amount": 200000.00,
        "due_date": (today + timedelta(days=20)).isoformat(),
        "status": "pending",
        "issued_date": (today - timedelta(days=10)).isoformat(),
    },
    # CUST-002: partially paid overdue
    {
        "id": "INV-004",
        "customer_id": "CUST-002",
        "invoice_number": "INV-2025-004",
        "amount": 320000.00,
        "due_date": (today - timedelta(days=30)).isoformat(),
        "status": "partially_paid",
        "issued_date": (today - timedelta(days=60)).isoformat(),
    },
    {
        "id": "INV-005",
        "customer_id": "CUST-002",
        "invoice_number": "INV-2025-005",
        "amount": 85000.00,
        "due_date": (today + timedelta(days=15)).isoformat(),
        "status": "pending",
        "issued_date": (today - timedelta(days=15)).isoformat(),
    },
    # CUST-003: all paid, good customer
    {
        "id": "INV-006",
        "customer_id": "CUST-003",
        "invoice_number": "INV-2025-006",
        "amount": 50000.00,
        "due_date": (today - timedelta(days=60)).isoformat(),
        "status": "paid",
        "issued_date": (today - timedelta(days=90)).isoformat(),
    },
    {
        "id": "INV-007",
        "customer_id": "CUST-003",
        "invoice_number": "INV-2025-007",
        "amount": 120000.00,
        "due_date": (today - timedelta(days=5)).isoformat(),
        "status": "paid",
        "issued_date": (today - timedelta(days=35)).isoformat(),
    },
    # CUST-004: heavily overdue
    {
        "id": "INV-008",
        "customer_id": "CUST-004",
        "invoice_number": "INV-2025-008",
        "amount": 500000.00,
        "due_date": (today - timedelta(days=95)).isoformat(),
        "status": "overdue",
        "issued_date": (today - timedelta(days=125)).isoformat(),
    },
    {
        "id": "INV-009",
        "customer_id": "CUST-004",
        "invoice_number": "INV-2025-009",
        "amount": 250000.00,
        "due_date": (today - timedelta(days=20)).isoformat(),
        "status": "overdue",
        "issued_date": (today - timedelta(days=50)).isoformat(),
    },
    # CUST-005: mix of pending and paid
    {
        "id": "INV-010",
        "customer_id": "CUST-005",
        "invoice_number": "INV-2025-010",
        "amount": 180000.00,
        "due_date": (today + timedelta(days=30)).isoformat(),
        "status": "pending",
        "issued_date": (today - timedelta(days=5)).isoformat(),
    },
    {
        "id": "INV-011",
        "customer_id": "CUST-005",
        "invoice_number": "INV-2025-011",
        "amount": 95000.00,
        "due_date": (today - timedelta(days=15)).isoformat(),
        "status": "paid",
        "issued_date": (today - timedelta(days=45)).isoformat(),
    },
]

PAYMENTS = [
    # Full payment for INV-002
    {
        "id": "PAY-001",
        "invoice_id": "INV-002",
        "amount": 75000.00,
        "payment_date": (today - timedelta(days=12)).isoformat(),
        "payment_method": "bank_transfer",
        "reference_number": "NEFT-20250301-001",
    },
    # Partial payment for INV-004
    {
        "id": "PAY-002",
        "invoice_id": "INV-004",
        "amount": 100000.00,
        "payment_date": (today - timedelta(days=25)).isoformat(),
        "payment_method": "upi",
        "reference_number": "UPI-20250215-002",
    },
    {
        "id": "PAY-003",
        "invoice_id": "INV-004",
        "amount": 50000.00,
        "payment_date": (today - timedelta(days=15)).isoformat(),
        "payment_method": "cash",
        "reference_number": "CASH-20250225-003",
    },
    # Full payments for CUST-003 invoices
    {
        "id": "PAY-004",
        "invoice_id": "INV-006",
        "amount": 50000.00,
        "payment_date": (today - timedelta(days=62)).isoformat(),
        "payment_method": "bank_transfer",
        "reference_number": "NEFT-20250110-004",
    },
    {
        "id": "PAY-005",
        "invoice_id": "INV-007",
        "amount": 120000.00,
        "payment_date": (today - timedelta(days=7)).isoformat(),
        "payment_method": "upi",
        "reference_number": "UPI-20250307-005",
    },
    # Small payment towards INV-001 (still overdue)
    {
        "id": "PAY-006",
        "invoice_id": "INV-001",
        "amount": 25000.00,
        "payment_date": (today - timedelta(days=30)).isoformat(),
        "payment_method": "card",
        "reference_number": "CARD-20250212-006",
    },
    # Full payment for INV-011
    {
        "id": "PAY-007",
        "invoice_id": "INV-011",
        "amount": 95000.00,
        "payment_date": (today - timedelta(days=10)).isoformat(),
        "payment_method": "bank_transfer",
        "reference_number": "NEFT-20250304-007",
    },
]


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/customers", tags=["External"])
def list_customers():
    return {"data": CUSTOMERS, "total": len(CUSTOMERS)}


@app.get("/customers/{customer_id}", tags=["External"])
def get_customer(customer_id: str):
    for c in CUSTOMERS:
        if c["id"] == customer_id:
            return {"data": c}
    return {"error": "Customer not found"}, 404


@app.get("/invoices", tags=["External"])
def list_invoices():
    return {"data": INVOICES, "total": len(INVOICES)}


@app.get("/invoices/{invoice_id}", tags=["External"])
def get_invoice(invoice_id: str):
    for inv in INVOICES:
        if inv["id"] == invoice_id:
            return {"data": inv}
    return {"error": "Invoice not found"}, 404


@app.get("/payments", tags=["External"])
def list_payments():
    return {"data": PAYMENTS, "total": len(PAYMENTS)}


@app.get("/payments/{payment_id}", tags=["External"])
def get_payment(payment_id: str):
    for p in PAYMENTS:
        if p["id"] == payment_id:
            return {"data": p}
    return {"error": "Payment not found"}, 404


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "external-accounting-system"}
