from fastapi import FastAPI, File, Form, UploadFile, HTTPException

app = FastAPI(title="SmartCrop AI inference boundary", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok", "mode": "DEMO_FALLBACK", "model_loaded": False}

@app.post("/api/predict")
async def predict(crop: str = Form(...), image: UploadFile = File(...)):
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    content = await image.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be smaller than 8 MB")
    return {"crop": crop, "problem": "Demo fallback assessment", "confidence": None, "severity": "UNKNOWN", "mode": "DEMO_FALLBACK", "message": "No trained agricultural model is configured. Do not treat this as a confirmed diagnosis."}
