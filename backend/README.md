# CRM Backend

FastAPI backend for the CRM Application.

## Setup

```bash
poetry install
```

## Development

```bash
poetry run fastapi dev app/main.py
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `POSTGRES_*` - PostgreSQL connection settings
- `MONGODB_*` - MongoDB connection settings
- `JWT_SECRET_KEY` - Secret key for JWT tokens
