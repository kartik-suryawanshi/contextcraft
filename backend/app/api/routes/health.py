from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database.connection import get_db
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as ex:
        db_status = f"unhealthy: {str(ex)}"

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "database": db_status,
        "mock_mode": settings.MOCK_MODE,
    }
