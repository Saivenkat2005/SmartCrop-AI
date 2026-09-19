from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'smartcrop.db'}"
SECRET_KEY = "smartcrop-demo-secret-change-me"
ALGORITHM = "HS256"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="FARMER")
    language: Mapped[str] = mapped_column(String(10), default="en")
    location: Mapped[str] = mapped_column(String(160), default="Guntur")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(Integer, index=True)
    crop: Mapped[str] = mapped_column(String(80))
    disease: Mapped[str] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(30))
    recommendation: Mapped[str] = mapped_column(Text)
    image_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class MarketPrice(Base):
    __tablename__ = "market_prices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    crop: Mapped[str] = mapped_column(String(80), index=True)
    market: Mapped[str] = mapped_column(String(100))
    district: Mapped[str] = mapped_column(String(100))
    price_per_kg: Mapped[float] = mapped_column(Float)
    min_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(80), default="DEMO DATA")
    data_status: Mapped[str] = mapped_column(String(20), default="DEMO")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ServiceItem(Base):
    __tablename__ = "service_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_type: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(160))
    location: Mapped[str] = mapped_column(String(160))
    detail: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float, default=0)
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    contact: Mapped[str] = mapped_column(String(30), default="9000000000")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(Integer, index=True)
    service_type: Mapped[str] = mapped_column(String(30))
    provider_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    crop: Mapped[str] = mapped_column(String(80))
    quantity: Mapped[str] = mapped_column(String(80))
    pickup_location: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    destination: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    email: Optional[str] = None
    language: str = "en"
    location: str = "Guntur"

class LoginRequest(BaseModel):
    phone: str
    password: str

class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: Optional[str] = None
    language: Optional[str] = None
    location: Optional[str] = None

class RequestCreate(BaseModel):
    service_type: str
    provider_id: Optional[int] = None
    crop: str = "Tomato"
    quantity: str
    pickup_location: Optional[str] = None
    destination: Optional[str] = None

app = FastAPI(title="SmartCrop AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def token_for(user: User) -> str:
    return jwt.encode({"sub": str(user.id), "exp": datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, algorithm=ALGORITHM)


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(db_session)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.get(User, int(payload["sub"]))
    except (jwt.PyJWTError, ValueError, TypeError):
        user = None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def seed_database():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.phone == "9000000001")):
            db.add(User(name="Demo Farmer", phone="9000000001", password_hash=pwd_context.hash("Farmer@123"), language="en", location="Guntur"))
            db.add(User(name="Admin", phone="9000000002", email="admin@smartcrop.ai", password_hash=pwd_context.hash("Admin@123"), role="ADMIN"))
        if not db.scalar(select(MarketPrice)):
            db.add_all([
                MarketPrice(crop="Tomato", market="Guntur", district="Guntur", price_per_kg=35, min_price=30, max_price=40),
                MarketPrice(crop="Tomato", market="Vijayawada", district="NTR", price_per_kg=32, min_price=28, max_price=38),
                MarketPrice(crop="Chilli", market="Guntur", district="Guntur", price_per_kg=118, min_price=105, max_price=130),
                MarketPrice(crop="Rice", market="Tenali", district="Guntur", price_per_kg=31, min_price=28, max_price=34),
            ])
        if not db.scalar(select(ServiceItem)):
            items = [
                ServiceItem(service_type="BUYER", name="ABC Fresh Foods", location="Guntur", detail="Tomato | 1,000 kg | ₹34/kg", price=34),
                ServiceItem(service_type="BUYER", name="Andhra Harvest Co.", location="Vijayawada", detail="Tomato, Chilli | 2,500 kg | ₹33/kg", price=33),
                ServiceItem(service_type="FPO", name="Guntur Vegetable FPO", location="Guntur", detail="450 members | Tomato, Chilli", price=0),
                ServiceItem(service_type="FPO", name="Krishna Farmers Collective", location="Tenali", detail="280 members | Rice, Maize", price=0),
                ServiceItem(service_type="STORAGE", name="Green Cold Storage", location="Guntur", detail="120 MT available | 4–8°C | ₹2/kg/day", price=2),
                ServiceItem(service_type="STORAGE", name="Harvest Shield Facility", location="Vijayawada", detail="80 MT available | 2–6°C | ₹2.5/kg/day", price=2.5),
                ServiceItem(service_type="LOGISTICS", name="Rural Route Transport", location="Guntur", detail="Mini truck | 1,000 kg | from ₹1,200", price=1200),
                ServiceItem(service_type="LOGISTICS", name="Kisan Mobility", location="Tenali", detail="Pickup vehicle | 500 kg | from ₹900", price=900),
            ]
            db.add_all(items)
        db.commit()

@app.on_event("startup")
def startup():
    seed_database()

@app.get("/health")
def health():
    return {"status": "ok", "service": "smartcrop-api"}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "phone": user.phone, "role": user.role, "language": user.language, "location": user.location}

@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(db_session)):
    if db.scalar(select(User).where(User.phone == payload.phone)):
        raise HTTPException(status_code=409, detail="A farmer with this phone already exists")
    user = User(**payload.model_dump(exclude={"password"}), password_hash=pwd_context.hash(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"token": token_for(user), "user": {"id": user.id, "name": user.name, "role": user.role, "language": user.language}}

@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(db_session)):
    user = db.scalar(select(User).where(User.phone == payload.phone))
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    return {"token": token_for(user), "user": {"id": user.id, "name": user.name, "role": user.role, "language": user.language}}

@app.get("/api/farmers/profile")
def profile(user: User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "phone": user.phone, "email": user.email, "language": user.language, "location": user.location}

@app.put("/api/farmers/profile")
def update_profile(payload: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    db.commit(); db.refresh(user)
    return {"id": user.id, "name": user.name, "language": user.language, "location": user.location}

@app.post("/api/diagnosis/analyze", status_code=201)
def analyze(crop: str = Form(...), image: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(db_session)):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Please upload a JPG, PNG, or WebP image")
    content = image.file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be smaller than 8 MB")
    diagnosis = Diagnosis(farmer_id=user.id, crop=crop, disease="Tomato Early Blight" if crop.lower() == "tomato" else f"{crop} health check", confidence=0.94, severity="Moderate", image_name=image.filename, recommendation="Remove severely affected leaves, keep the field clean, and avoid prolonged leaf wetness. Follow locally approved guidance and product labels.")
    db.add(diagnosis); db.commit(); db.refresh(diagnosis)
    return {"id": diagnosis.id, "crop": diagnosis.crop, "disease": diagnosis.disease, "confidence": diagnosis.confidence, "severity": diagnosis.severity, "model": "Demo fallback (YOLOv8 interface ready)", "data_status": "DEMO AI", "symptoms": ["Dark spots on older leaves", "Yellowing around affected areas"], "immediate_action": ["Remove severely affected leaves", "Maintain field hygiene", "Avoid overhead watering"], "prevention": ["Monitor plants regularly", "Keep spacing between plants"], "warning": "This is AI-assisted information, not a confirmed diagnosis. For chemical control, follow product labels and local agricultural guidance."}

@app.get("/api/diagnosis/history")
def diagnosis_history(user: User = Depends(current_user), db: Session = Depends(db_session)):
    records = db.scalars(select(Diagnosis).where(Diagnosis.farmer_id == user.id).order_by(Diagnosis.created_at.desc())).all()
    return [{"id": item.id, "crop": item.crop, "disease": item.disease, "confidence": item.confidence, "severity": item.severity, "created_at": item.created_at.isoformat()} for item in records]

@app.get("/api/market/prices")
def market_prices(crop: Optional[str] = None, db: Session = Depends(db_session)):
    query = select(MarketPrice)
    if crop: query = query.where(MarketPrice.crop.ilike(f"%{crop}%"))
    return [{"id": x.id, "crop": x.crop, "market": x.market, "district": x.district, "price_per_kg": x.price_per_kg, "min_price": x.min_price, "max_price": x.max_price, "source": x.source, "data_status": x.data_status, "updated_at": x.updated_at.isoformat()} for x in db.scalars(query).all()]

@app.get("/api/services/{service_type}")
def services(service_type: str, db: Session = Depends(db_session)):
    items = db.scalars(select(ServiceItem).where(ServiceItem.service_type == service_type.upper())).all()
    return [{"id": x.id, "name": x.name, "location": x.location, "detail": x.detail, "price": x.price, "verified": x.verified, "contact": x.contact} for x in items]

@app.post("/api/requests", status_code=201)
def create_request(payload: RequestCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    item = ServiceRequest(farmer_id=user.id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "service_type": item.service_type, "status": item.status, "message": "Request created successfully"}

@app.get("/api/requests")
def requests(user: User = Depends(current_user), db: Session = Depends(db_session)):
    records = db.scalars(select(ServiceRequest).where(ServiceRequest.farmer_id == user.id).order_by(ServiceRequest.created_at.desc())).all()
    return [{"id": x.id, "service_type": x.service_type, "crop": x.crop, "quantity": x.quantity, "status": x.status, "created_at": x.created_at.isoformat()} for x in records]
