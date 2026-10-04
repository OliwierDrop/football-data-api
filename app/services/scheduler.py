import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database.session import SessionLocal
from app.services.sync import SyncService

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def _run_sync_job() -> None:
    logger.info("Starting scheduled sync")
    db = SessionLocal()
    try:
        result = SyncService(db).sync_all()
        logger.info("Scheduled sync finished: %s", result)
    except Exception:
        logger.exception("Scheduled sync crashed")
    finally:
        db.close()


def start_scheduler() -> None:
    if not settings.run_scheduler:
        logger.info("Scheduler disabled")
        return
    if scheduler.running:
        return
    scheduler.add_job(
        _run_sync_job,
        trigger="interval",
        minutes=settings.sync_interval_minutes,
        id="football_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started – sync every %s minutes",
        settings.sync_interval_minutes,
    )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
