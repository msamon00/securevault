from fastapi import FastAPI
from app.database import Base, engine
from app.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecureVault", version="0.1.0")

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}