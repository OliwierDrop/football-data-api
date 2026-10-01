from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import ScrapeRun
from app.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)) -> HealthOut:
    database_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_status = "disconnected"

    last_success: datetime | None = None
    if database_status == "connected":
        last_success = db.scalars(
            select(ScrapeRun.finished_at)
            .where(ScrapeRun.status == "success")
            .order_by(ScrapeRun.finished_at.desc())
            .limit(1)
        ).first()

    return HealthOut(
        status="ok" if database_status == "connected" else "degraded",
        database=database_status,
        last_successful_sync=last_success,
    )
