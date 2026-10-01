from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.repositories.teams import StandingRepository, TeamRepository
from app.schemas import StandingOut

router = APIRouter(prefix="/api/standings", tags=["standings"])


@router.get("", response_model=list[StandingOut])
def list_standings(db: Session = Depends(get_db)) -> list[dict]:
    repo = StandingRepository(db)
    standings = repo.list_latest()
    # Prefer standings that include the primary team
    primary = TeamRepository(db).get_by_external_id(settings.team_external_id)
    if primary is not None:
        primary_rows = [s for s in standings if s.team_id == primary.id]
        if primary_rows:
            competition_id = primary_rows[0].competition_id
            season_id = primary_rows[0].season_id
            standings = [
                s
                for s in standings
                if s.competition_id == competition_id and s.season_id == season_id
            ]
    return [repo.serialize(s) for s in standings]
