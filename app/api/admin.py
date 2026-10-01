from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.sync import SyncService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/sync")
def trigger_sync(db: Session = Depends(get_db)) -> dict:
    """Manual sync trigger for development / ops. Does not scrape on regular API reads."""
    return SyncService(db).sync_all()
