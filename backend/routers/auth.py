from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from models.database import get_db
from models.models import User, PlanType
from config import get_settings
from services.email_service import send_welcome_email
import json

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    organization_name: str
    organization_type: str  # nonprofit, contractor, consultant, other
    focus_areas: list[str] = []
    states: list[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter_by(id=int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", response_model=Token)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        organization_name=req.organization_name,
        organization_type=req.organization_type,
        focus_areas=json.dumps(req.focus_areas),
        states=json.dumps(req.states),
        plan=PlanType.starter,
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_welcome_email(user.email, user.organization_name or user.email)

    token = create_token({"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user={"id": user.id, "email": user.email, "organization_name": user.organization_name, "plan": user.plan},
    )


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user={"id": user.id, "email": user.email, "organization_name": user.organization_name, "plan": user.plan},
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    import json
    return {
        "id": current_user.id,
        "email": current_user.email,
        "organization_name": current_user.organization_name,
        "organization_type": current_user.organization_type,
        "focus_areas": json.loads(current_user.focus_areas) if current_user.focus_areas else [],
        "states": json.loads(current_user.states) if current_user.states else [],
        "plan": current_user.plan,
        "trial_ends_at": current_user.trial_ends_at.isoformat() if current_user.trial_ends_at else None,
    }
