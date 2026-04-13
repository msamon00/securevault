from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import time
from collections import defaultdict
from . import models, schemas
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .database import get_db
from .config import settings

router = APIRouter()

# Simple in-memory rate limiter
# Tracks failed login attempts per IP address
_failed_attempts: dict = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300  # 5 minutes

def check_rate_limit(ip: str):
    """Block IPs that have too many failed login attempts."""
    now = time.time()
    # Remove attempts outside the current window
    _failed_attempts[ip] = [
        t for t in _failed_attempts[ip]
        if now - t < WINDOW_SECONDS
    ]
    if len(_failed_attempts[ip]) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again in 5 minutes."
        )

def record_failed_attempt(ip: str):
    """Record a failed login attempt for an IP."""
    _failed_attempts[ip].append(time.time())


# ── Registration ────────────────────────────────────────────────
@router.post("/auth/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register the vault owner. Only one user is allowed.
    This endpoint disables itself after the first registration.
    """
    existing_users = db.query(models.User).count()
    if existing_users > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is closed. This vault already has an owner."
        )

    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )

    hashed = hash_password(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ── Login ────────────────────────────────────────────────────────
@router.post("/auth/login", response_model=schemas.Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate and return a JWT token."""
    ip = request.client.host
    check_rate_limit(ip)

    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        record_failed_attempt(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ── Protected test route ─────────────────────────────────────────
@router.get("/auth/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    """Returns the current authenticated user. Used to verify token validity."""
    return {
        "username": current_user.username,
        "created_at": current_user.created_at
    }