# Django E-Commerce Platform

A modular, full-featured e-commerce application built with Django and Django REST Framework.  
This project demonstrates best practices in project structure, Docker deployment, CI/CD, testing, and code quality.

---

## Table of Contents

- [About](#about)  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
  - [Development Setup (Docker Compose)](#development-setup-docker-compose)  
  - [Staging/Production Setup (Docker Compose)](#stagingproduction-setup-docker-compose)  
- [Environment Variables](#environment-variables)  
- [Usage](#usage)  
  - [Database Migrations & Superuser](#database-migrations--superuser)  
  - [Shop Management Commands](#shop-management-commands)  
- [Running Tests](#running-tests)  
- [API Documentation](#api-documentation)  
- [CI/CD Pipeline](#cicd-pipeline)  
- [Code Style](#code-style)  
- [License](#license)  

---

## About

This repository implements an **e-commerce platform** with these Django apps:

- **accounts**: Custom user model, registration, email confirmation, JWT & token-based authentication, password reset.  
- **cart**: Session- and database-backed shopping cart with AJAX and REST endpoints.  
- **shop**: Product catalog, nested categories, dynamic features & options, search, filtering, pagination, wishlist.  
- **order**: Checkout workflow, coupon validation, order and order-item models, transactional stock updates via signals.  
- **payment**: ZarinPal Sandbox integration, payment request & verification, order status transitions.  
- **review**: User-submitted product reviews, approval workflow, average rating aggregation via signals.  
- **dashboard**: Separate admin & customer dashboards—CRUD interfaces and REST APIs for all core models.  
- **website**: Public pages (home, about, contact form, newsletter subscription) with both template views and REST endpoints.  

---

## Features

- User registration, email confirmation, login/logout (session & JWT).  
- Fully featured shopping cart (add/remove/update items, summary).  
- Product listing: grid view, detail view, filtering by category, price, and custom features.  
- Wishlist management (add/remove) via AJAX and API.  
- Checkout process: address selection, coupon application, cart validation.  
- Payment integration with ZarinPal Sandbox (request, authority, verify).  
- Review system: submit, moderated approval, star-rating statistics.  
- Admin & customer dashboards with Django class-based views and DRF viewsets.  
- Celery for asynchronous tasks (e.g. canceling stale orders) and django-celery-beat for scheduled jobs.  
- Dockerized for development & production, NGINX as reverse proxy, PostgreSQL, Redis, SMTP4DEV.  
- Comprehensive test suite covering models, forms, and template-based views.  
- Interactive API documentation with Swagger UI and ReDoc.  
- CI/CD pipeline via GitHub Actions automating build, test, and deploy.  

---

## Prerequisites

- Python 3.8+  
- Docker & Docker Compose  
- PostgreSQL  
- Redis  

---

## Installation

### Development Setup (Docker Compose)

```bash
docker-compose up --build
```

- Django backend on `http://localhost:8000`  
- PostgreSQL on port `5432`  
- pgAdmin on port `5050`  
- Redis on port `6379`  
- SMTP4DEV on port `5000` (web) and `25` (SMTP)  
- Celery worker & beat services  

### Staging/Production Setup (Docker Compose)

```bash
docker-compose -f docker-compose-stage.yml up -d --build
```

- Django served by Gunicorn  
- NGINX as reverse proxy for static/media and backend  
- Persistent volumes for static files, media, and PostgreSQL data  

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```dotenv
SECRET_KEY=...
DEBUG=False

DATABASE_NAME=...
DATABASE_USER=...
DATABASE_PASSWORD=...
DATABASE_HOST=db
DATABASE_PORT=5432

REDIS_URL=redis://redis:6379/0

MERCHANT_ID=<ZARINPAL_SANDBOX_MERCHANT_ID>

EMAIL_HOST=...
EMAIL_PORT=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

---

## Usage

### Database Migrations & Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Shop Management Commands

```bash
# Create default category hierarchy
python manage.py create_default_categories

# Load default features from text file
python manage.py create_default_features

# Generate <count> random products per subcategory
python manage.py create_products 20
```

---

## Running Tests

All tests use Django’s built-in test runner. To run every test:

```bash
python manage.py test
```

To run tests for a single app:

```bash
python manage.py test shop
python manage.py test accounts
# etc.
```

---

## API Documentation

After starting the server, interactive API docs are available:

- Swagger UI: `http://<host>/swagger/`  
- ReDoc UI:   `http://<host>/redoc/`  
- OpenAPI JSON: `http://<host>/swagger/output.json`  

> Access to documentation is protected by the `IsAdminOrSuperUser` permission.

---

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/test-and-deploy.yml`) runs on pushes and pull requests to `main`:

1. Checkout repository  
2. Set up Docker Buildx & Docker Compose  
3. Build and start services using `docker-compose-stage.yml`  
4. Execute `python manage.py test` inside the backend container  
5. On success, SSH into your VPS and pull changes, then rebuild and restart services  

---

## Code Style

- **Flake8** configured in `.flake8`:
  ```ini
  [flake8]
  max-line-length = 79
  exclude = __pycache__,__init__
  ```
- Run linting locally:
  ```bash
  flake8
  ```

---

## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.
