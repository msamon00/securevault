from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import time
import base64
import json
from collections import defaultdict
from . import models, schemas
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .crypto import derive_key, generate_salt, encrypt, decrypt
from .database import get_db
from .config import settings

router = APIRouter()

# Simple in-memory rate limiter
_failed_attempts: dict = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300

def check_rate_limit(ip: str):
    now = time.time()
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
    _failed_attempts[ip].append(time.time())


# ── Registration ─────────────────────────────────────────────────
@router.post("/auth/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_users = db.query(models.User).count()
    if existing_users > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is closed. This vault already has an owner."
        )

    kdf_salt = generate_salt()
    kdf_salt_b64 = base64.b64encode(kdf_salt).decode()

    hashed = hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        hashed_password=hashed,
        kdf_salt=kdf_salt_b64
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    encryption_key = derive_key(user_data.password, kdf_salt)
    encryption_key_b64 = base64.b64encode(encryption_key).decode()

    access_token = create_access_token(data={
        "sub": new_user.username,
        "key": encryption_key_b64
    })
    return {"access_token": access_token, "token_type": "bearer"}


# ── Login ─────────────────────────────────────────────────────────
@router.post("/auth/login", response_model=schemas.Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
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

    kdf_salt = base64.b64decode(user.kdf_salt.encode())
    encryption_key = derive_key(form_data.password, kdf_salt)
    encryption_key_b64 = base64.b64encode(encryption_key).decode()

    access_token = create_access_token(
        data={
            "sub": user.username,
            "key": encryption_key_b64
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ── Get current user ──────────────────────────────────────────────
@router.get("/auth/me")
def get_me(current_user=Depends(get_current_user)):
    user, _ = current_user
    return {
        "username": user.username,
        "created_at": user.created_at
    }


# ── Vault endpoints ───────────────────────────────────────────────
@router.post("/vault", response_model=schemas.VaultEntryResponse)
def create_entry(
    entry_data: schemas.VaultEntryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new encrypted vault entry."""
    user, encryption_key = current_user

    # Serialize all entry fields to JSON, then encrypt the whole blob
    plaintext = json.dumps({
        "username": entry_data.username,
        "password": entry_data.password,
        "url": entry_data.url,
        "notes": entry_data.notes
    })

    ciphertext_b64, iv_b64 = encrypt(plaintext, encryption_key)

    entry = models.VaultEntry(
        user_id=user.id,
        title=entry_data.title,
        encrypted_data=ciphertext_b64,
        iv=iv_b64
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Decrypt to return the full entry in the response
    decrypted = json.loads(decrypt(entry.encrypted_data, entry.iv, encryption_key))
    return schemas.VaultEntryResponse(
        id=entry.id,
        title=entry.title,
        created_at=entry.created_at,
        **decrypted
    )


@router.get("/vault", response_model=list[schemas.VaultEntryResponse])
def list_entries(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """List all vault entries, decrypted."""
    user, encryption_key = current_user

    entries = db.query(models.VaultEntry).filter(
        models.VaultEntry.user_id == user.id
    ).all()

    results = []
    for entry in entries:
        decrypted = json.loads(decrypt(entry.encrypted_data, entry.iv, encryption_key))
        results.append(schemas.VaultEntryResponse(
            id=entry.id,
            title=entry.title,
            created_at=entry.created_at,
            **decrypted
        ))
    return results


@router.get("/vault/{entry_id}", response_model=schemas.VaultEntryResponse)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get a single vault entry by ID."""
    user, encryption_key = current_user

    entry = db.query(models.VaultEntry).filter(
        models.VaultEntry.id == entry_id,
        models.VaultEntry.user_id == user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")

    decrypted = json.loads(decrypt(entry.encrypted_data, entry.iv, encryption_key))
    return schemas.VaultEntryResponse(
        id=entry.id,
        title=entry.title,
        created_at=entry.created_at,
        **decrypted
    )


@router.put("/vault/{entry_id}", response_model=schemas.VaultEntryResponse)
def update_entry(
    entry_id: int,
    entry_data: schemas.VaultEntryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Update an existing vault entry."""
    user, encryption_key = current_user

    entry = db.query(models.VaultEntry).filter(
        models.VaultEntry.id == entry_id,
        models.VaultEntry.user_id == user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")

    plaintext = json.dumps({
        "username": entry_data.username,
        "password": entry_data.password,
        "url": entry_data.url,
        "notes": entry_data.notes
    })

    ciphertext_b64, iv_b64 = encrypt(plaintext, encryption_key)
    entry.title = entry_data.title
    entry.encrypted_data = ciphertext_b64
    entry.iv = iv_b64
    db.commit()
    db.refresh(entry)

    decrypted = json.loads(decrypt(entry.encrypted_data, entry.iv, encryption_key))
    return schemas.VaultEntryResponse(
        id=entry.id,
        title=entry.title,
        created_at=entry.created_at,
        **decrypted
    )


@router.delete("/vault/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Delete a vault entry."""
    user, encryption_key = current_user

    entry = db.query(models.VaultEntry).filter(
        models.VaultEntry.id == entry_id,
        models.VaultEntry.user_id == user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")

    db.delete(entry)
    db.commit()
    return {"detail": "Entry deleted successfully."}