# AI Architecture

The crop diagnosis surface is designed around an explicit model boundary. Uploads are validated for type and size before inference. The current result is a deterministic demo fallback, labeled in the UI and API. It is not a trained disease classifier.

The `ai` service exposes `POST /api/predict` and `GET /health`. A future model adapter should return only supported classes, calibrated confidence, severity rules, model version, and an audit record. Treatment guidance remains structured and includes a safety warning to follow local agricultural guidance and product labels.
