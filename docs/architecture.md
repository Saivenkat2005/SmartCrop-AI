# Architecture

```mermaid
flowchart TD
  Farmer --> Frontend[React PWA]
  Frontend --> Backend[FastAPI REST API]
  Frontend --> Outbox[Local storage outbox]
  Backend --> SQLite[(SQLite)]
  Backend -. future model call .-> AI[FastAPI AI boundary]
  Backend -. future provider .-> Market[Verified market provider]
```

The backend is intentionally modular and small for a hackathon: API route -> persistence/service logic -> SQLite. The AI boundary can later host a MobileNet, EfficientNet, or validated agricultural YOLO pipeline without changing the farmer-facing contract.
