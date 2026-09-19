# Deployment

Install Docker Desktop, then run:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health
- AI health: http://localhost:8001/health

The backend SQLite file is stored in the `backend_data` Docker volume. Replace demo secrets, add a managed database, and configure a real model before production use.
