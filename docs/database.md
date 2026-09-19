# Database

The hackathon build uses SQLite at `backend/smartcrop.db` and creates tables on startup. Core entities are users, diagnoses, market prices, service items, and service requests. Foreign-key IDs and timestamps are included where relationships are required. A PostgreSQL deployment can replace the SQLAlchemy URL and add Alembic migrations without changing the API layer.
