# API

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET|PUT /api/farmers/profile`
- `POST /api/diagnosis/analyze`
- `GET /api/diagnosis/history`
- `GET /api/market/prices?crop=Tomato`
- `GET /api/services/BUYER|FPO|STORAGE|LOGISTICS`
- `POST /api/requests`
- `GET /api/requests`
- `GET /health`

Authenticated calls use `Authorization: Bearer <token>`.
