from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    kdf_salt = Column(String, nullable=False, server_default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VaultEntry(Base):
    __tablename__ = "vault_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    encrypted_data = Column(String, nullable=False)
    iv = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())