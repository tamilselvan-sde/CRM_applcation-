# CRM Application

A production-grade Customer Relationship Management (CRM) web application with React frontend, FastAPI backend, and containerized infrastructure using Podman.

## Features

- **User & Role Management**: Authentication & authorization with roles (admin, manager, staff, viewer)
- **Customer Management**: Full CRUD operations for customer records
- **Product & Service Management**: Manage products and services catalog
- **Invoice Management**: Create invoices with automatic PDF generation
- **Role-Aware UI**: UI components adapt based on user permissions
- **PDF Invoice Download**: One-click download of professionally formatted invoices

## Tech Stack

- **Frontend**: React with Vite, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.12), JWT authentication
- **Databases**: PostgreSQL (CRM data), MongoDB (roles & permissions)
- **Infrastructure**: Podman containers with podman-compose
- **PDF Generation**: ReportLab

## Architecture

```
React UI  →  FastAPI  →  PostgreSQL (CRM Data)
                ↘
                 MongoDB (Roles & Permissions)
```

## Quick Start

### Prerequisites

- Podman and podman-compose installed
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tamilselvan-sde/CRM_applcation-.git
   cd CRM_applcation-
   ```

2. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start all services:
   ```bash
   podman-compose up
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Admin User

After starting the application, you can log in with:
- Email: `admin@crm.local`
- Password: `admin123`

## Project Structure

```
CRM_applcation-/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   ├── context/       # React context (auth)
│   │   └── styles/        # CSS styles
│   ├── Dockerfile
│   └── nginx.conf
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── routers/       # API routes
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── middleware/    # Auth middleware
│   │   └── database/      # DB connections
│   └── Dockerfile
├── tests/                 # E2E test suite
├── docs/
│   └── schemas/           # Database initialization scripts
├── podman-compose.yml     # Container orchestration
└── .env.example           # Environment template
```

## User Roles

| Role    | Description                                      |
|---------|--------------------------------------------------|
| admin   | Full system access - manage users and all data   |
| manager | Manage customers, products, and invoices         |
| staff   | Create invoices and view data                    |
| viewer  | Read-only access, can download invoice PDFs      |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/users` - List all users (admin only)
- `PUT /api/auth/users/{id}` - Update user (admin only)
- `DELETE /api/auth/users/{id}` - Delete user (admin only)

### Customers
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/{id}` - Get customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Invoices
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Create invoice
- `GET /api/invoices/{id}` - Get invoice
- `PUT /api/invoices/{id}` - Update invoice
- `DELETE /api/invoices/{id}` - Delete invoice
- `GET /api/invoices/{id}/pdf` - Download invoice PDF

## Running Tests

The E2E test suite requires the application to be running:

```bash
# Start the application
podman-compose up -d

# Install test dependencies
cd tests
pip install -r requirements.txt

# Run tests
pytest

# Run specific test file
pytest test_login.py

# Run with verbose output
pytest -v
```

## Development

### Backend Development

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` for all available configuration options:

- `POSTGRES_*` - PostgreSQL connection settings
- `MONGODB_*` - MongoDB connection settings
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

## License

MIT
