# SmartCrop AI

SmartCrop AI is a farmer-first hackathon MVP for the journey from crop care to market access: **Diagnose -> Decide -> Sell**.

## Included

- React + TypeScript farmer interface with mobile-first layout
- FastAPI + SQLite REST API with JWT authentication and bcrypt password hashing
- Seeded demo farmer, market prices, buyers, FPOs, cold storage, logistics, and request records
- AI diagnosis upload flow with an explicit demo fallback label and structured treatment guidance
- English, Telugu, and Hindi UI labels
- PWA service worker, offline status, and local outbox foundation
- Separate AI inference boundary service ready for a trained model
- Docker Compose deployment

## Run

Prerequisite: Docker Desktop.

```bash
docker compose up --build
```

Open http://localhost:3000. The API is at http://localhost:8000/docs and the AI boundary is at http://localhost:8001/docs.

Demo farmer: `9000000001` / `Farmer@123`

All market, buyer, storage, and logistics records in the seeded environment are labeled `DEMO DATA`. The diagnosis is `DEMO AI MODE`; no trained agricultural model is bundled.

## Development

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

cd frontend
npm install
npm run dev
```

## Product flow

1. Sign in or register.
2. Choose a language from the top bar.
3. Upload a crop image and review the preliminary assessment.
4. Read structured symptoms, immediate actions, prevention, and safety guidance.
5. Compare indicative market data.
6. Send interest to buyers or request storage and transport.
7. Review submitted requests.

## Limitations and roadmap

The project deliberately does not claim live market prices, confirmed disease diagnosis, real-time transport tracking, or full offline AI inference. Production work would add a verified market provider, a validated crop model, expert review workflows, PostgreSQL migrations, stronger device sync conflict handling, and field trials.
