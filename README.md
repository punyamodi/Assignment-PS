# PaySaathi — Integration Engineer Take-Home Assessment

A service that integrates with an external accounting system, syncs customer/invoice/payment data locally, and exposes financial insight APIs for receivables analysis.

---

## 🏗️ Architecture

```
┌──────────────────────┐        ┌──────────────────────────────────────┐
│  External Accounting │  HTTP  │     PaySaathi Integration Service    │
│  System (Mock API)   │◄──────►│                                      │
│  Port 8001           │        │  ┌──────────┐   ┌────────────────┐  │
│  /customers          │        │  │ Sync      │──►│ SQLite DB      │  │
│  /invoices           │        │  │ Service   │   │  - customers   │  │
│  /payments           │        │  └──────────┘   │  - invoices    │  │
└──────────────────────┘        │                  │  - payments    │  │
                                │  ┌──────────┐   │  - sync_log    │  │
         Clients ──────────────►│  │ Insight   │──►│                │  │
         (REST API)             │  │ Service   │   └────────────────┘  │
                                │  └──────────┘                        │
                                │  Port 8000                           │
                                └──────────────────────────────────────┘
```

## 🚀 How to Run

### Prerequisites
- Python 3.11+
- pip

### 1. Install dependencies
```bash
cd paysaathi
pip install -r requirements.txt
```

### 2. Start the Mock External API (Terminal 1)
```bash
uvicorn app.external.mock_api:app --port 8001
```
This simulates the external accounting system on `http://localhost:8001`.

### 3. Start the PaySaathi Service (Terminal 2)
```bash
uvicorn app.main:app --port 8000 --reload
```

### 4. Trigger a Data Sync
```bash
curl -X POST http://localhost:8000/sync/
```
This fetches all customers, invoices, and payments from the external system and stores them locally.

### 5. Query Insights
```bash
# Outstanding balances per customer
curl http://localhost:8000/insights/outstanding-balances

# Overdue invoices
curl http://localhost:8000/insights/overdue-invoices

# Customer credit summary
curl http://localhost:8000/insights/customer/CUST-001/credit-summary

# Receivables aging report
curl http://localhost:8000/insights/aging-report
```

### 6. Interactive API Docs
Open **http://localhost:8000/docs** for Swagger UI with all endpoints documented.

### 7. Run Tests
```bash
python -m pytest tests/ -v
```

---

## 📐 Key Design Decisions

### 1. **Python + FastAPI**
Chosen for async support, automatic OpenAPI docs, Pydantic validation, and clean dependency injection — all critical for an integration service that talks to external APIs.

### 2. **SQLite + SQLAlchemy**
SQLite requires zero infrastructure setup while SQLAlchemy's ORM provides a clean abstraction. The `DATABASE_URL` setting makes it trivial to swap to PostgreSQL for production.

### 3. **Upsert-based Sync (Idempotent)**
The sync service uses an upsert pattern (check if exists → update or insert). This means re-running sync is safe and produces consistent results, handling the common integration challenge of duplicate data.

### 4. **Sync Log Table**
Every sync operation is recorded in `sync_log` with status, record count, timestamps, and any errors. This provides auditability and helps debug integration failures.

### 5. **Separate Mock API**
The external accounting system runs as a separate FastAPI service. This simulates real-world integration where the external system is an independent service. It can be replaced with a real API by changing `EXTERNAL_API_BASE_URL` in config.

### 6. **Risk Rating Algorithm**
Customer risk is computed from `overdue_amount / total_invoiced`:
- **Low**: ≤ 20% overdue ratio
- **Medium**: 20–50% overdue ratio
- **High**: > 50% overdue ratio

### 7. **Aging Buckets**
Standard receivables aging: 0–30, 31–60, 61–90, 90+ days — matching accounting industry conventions.

### 8. **Clean Separation of Concerns**
```
app/
├── api/            # Route handlers (thin controllers)
├── services/       # Business logic (sync + insights)
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response models
├── external/       # Mock external system
├── config.py       # Settings (env-based)
└── database.py     # DB engine + session
```

---

## 📝 Assumptions

1. **External API returns all records** — The mock API returns complete datasets on each call (no pagination). In production, this would need cursor-based pagination.
2. **Invoice status comes from external system** — We trust the `status` field from the external API but also compute overdue status locally based on `due_date` and payments.
3. **Payments are linked to invoices** — Every payment references an invoice. We don't handle unlinked payments.
4. **Currency is INR** — All amounts are in a single currency (Indian Rupees). Multi-currency support would require exchange rate handling.
5. **Sync is triggered manually** — Via `POST /sync/`. In production, this would be a scheduled job (cron/Celery).
6. **Outstanding = Invoiced - Paid** — Simple calculation. Doesn't account for credit notes, discounts, or write-offs.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sync/` | Trigger full data sync from external system |
| `GET` | `/insights/outstanding-balances` | Per-customer outstanding balances |
| `GET` | `/insights/overdue-invoices` | All overdue unpaid invoices |
| `GET` | `/insights/customer/{id}/credit-summary` | Full credit profile with risk rating |
| `GET` | `/insights/aging-report` | Receivables aging buckets |
| `GET` | `/data/customers` | List all synced customers |
| `GET` | `/data/invoices?customer_id=X` | List invoices (optional filter) |
| `GET` | `/data/payments?invoice_id=X` | List payments (optional filter) |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

---

## 🧪 Test Coverage

- **23 tests** covering:
  - Outstanding balance calculations
  - Overdue invoice detection
  - Customer credit summaries with risk ratings
  - Aging report bucket classification
  - API endpoint responses and error handling
  - Data browsing endpoints

```
tests/
├── conftest.py          # Fixtures (in-memory DB, test client)
├── test_insights.py     # Insight service unit tests
└── test_api.py          # API integration tests
```
