# b2b-multi-vendor-procurement-catalog-backend
Production-style Django REST Framework backend for B2B multi-vendor procurement and catalog management, including JWT auth, vendor onboarding, product catalog, order workflow, invoices, Redis caching, Celery background jobs, PostgreSQL and Docker.

# ProcureFlow — B2B Multi-Vendor Procurement & Catalog Backend

Production-grade REST API backend for a B2B multi-vendor procurement platform.
Vendors list products, buyers raise purchase orders with internal approval,
and the system handles order lifecycle, invoicing with PDF generation,
payments, notifications, async emails and scheduled reporting.

## Tech Stack

- **Django 4.2 + Django REST Framework** — API layer
- **PostgreSQL** — production database (SQLite option for zero-setup dev)
- **Redis** — caching + Celery broker
- **Celery + Celery Beat** — async emails + scheduled daily sales report
- **SimpleJWT** — token authentication with role-based access
- **xhtml2pdf** — invoice PDF generation
- **Django Signals** — event-driven notifications
- **Docker + Nginx + Gunicorn** — deployment ready

## Key Features

- Custom User model with JWT auth (register / login / refresh / logout)
- Role-based access: `admin`, `buyer`, `vendor`, `finance`
- Vendor onboarding with KYC documents + admin approval workflow
- Product catalog with images, tags, filtering, search, pagination
- Order management with a strict **state machine** (11 statuses)
- Stock reservation with `select_for_update` (no race conditions)
- Invoice generation with **formatted PDF** + payment recording
- **Redis caching** on product listing & vendor dashboard with pattern-based invalidation
- **Celery tasks**: order confirmation + invoice emails with PDF attachment
- **Celery Beat**: daily sales report (Asia/Kolkata timezone)
- **Django signals**: auto notifications on order / vendor / invoice events
- Seed data system — one command demo setup

## Quick Start (Zero Setup)

```bash
git clone <your-repo-url>
cd b2b-multi-vendor-procurement-catalog-backend

python -m venv project_venv
source project_venv/bin/activate        # Windows: project_venv\Scripts\activate
pip install -r requirements/base.txt

cp .env.example .env                    # USE_SQLITE=True by default

python manage.py migrate
python manage.py seed_data              # demo users, vendors, products, orders, invoice
python manage.py runserver
```

Optional (async + scheduled tasks):

```bash
celery -A config worker -l info         # terminal 2
celery -A config beat -l info           # terminal 3
```

For real emails, set Gmail app password in `.env` (see `.env.example`).
For PostgreSQL, set `USE_SQLITE=False` and fill DB_* values.

## Demo Credentials

| Role   | Email                  | Password     |
|--------|------------------------|--------------|
| Admin  | shivbhatt0111@gmail.com | Password@123 |
| Buyer  | shivbhatt0112@gmail.com | Password@123 |
| Vendor | shivbhatt0113@gmail.com | Password@123 |

## API Overview (`/api/v1/`)

| Area | Endpoints |
|------|-----------|
| Auth | `auth/register/`, `auth/login/`, `auth/refresh/`, `auth/logout/`, `auth/profile/` |
| Vendors | `vendors/register/`, `vendors/profile/`, `vendors/dashboard/`, `vendors/list/`, `vendors/<id>/approve/`, `vendors/kyc/` |
| Catalog | `catalog/categories/`, `catalog/tags/`, `catalog/products/`, `catalog/products/create/`, `catalog/products/<slug>/`, `.../update/`, `.../delete/`, `.../images/` |
| Orders | `orders/addresses/`, `orders/create/`, `orders/`, `orders/<number>/`, `.../approve/`, `.../status/`, `.../history/` |
| Invoices | `invoices/create/`, `invoices/`, `invoices/<number>/`, `.../pdf/`, `.../payments/` |
| Notifications | `notifications/`, `notifications/<id>/read/`, `notifications/mark-all-read/` |

Full request/response examples: see `postman/` collection.

## Order State Machine

```
draft → pending_approval → approved → sent_to_vendor → accepted_by_vendor
      → partially_delivered → delivered → invoiced → completed
(any stage) → cancelled | pending_approval → rejected
```

## Architecture Highlights

- **Services layer** (`services.py`) keeps business logic out of views
- **State machine** module enforces valid order transitions
- **Cache-aside pattern** with `delete_pattern` invalidation on writes
- **Idempotent seeders** (`python manage.py seed_data --app <name>`)
- Consistent response envelope: `{success, message, data, errors}`

## Project Structure

```
apps/
├── accounts/       # custom user, JWT auth
├── vendors/        # vendor onboarding, KYC, approval, dashboard
├── catalog/        # categories, products, images, caching
├── orders/         # orders, state machine, stock handling
├── invoices/       # invoices, payments, PDF generation
├── notifications/  # signals-driven notifications
├── reports/        # Celery Beat scheduled reports
└── core/           # health, pagination, renderer, seed command
seeders/            # per-app demo data
config/             # settings (base/dev/prod), celery, urls
```


## Running Tests

```bash
pip install -r requirements/dev.txt
pytest tests/ -v


# ProcureFlow — B2B Multi-Vendor Procurement & Catalog Backend

![CI](https://github.com/shivmohan8085/b2b-multi-vendor-procurement-catalog-backend/actions/workflows/ci.yml/badge.svg)
Production-grade REST API backend for a B2B multi-vendor procurement platform.


## Docker Setup (Production-Ready)
# Build and start all containers
docker compose up --build

# Services running:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - Django + Gunicorn (port 8000)
# - Celery Worker
# - Celery Beat