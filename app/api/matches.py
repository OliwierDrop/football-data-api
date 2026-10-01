from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.repositories.matches import MatchRepository, serialize_match
from app.repositories.teams import TeamRepository
from app.schemas import MatchOut

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _primary_team_id(db: Session) -> int | None:
    team = TeamRepository(db).get_by_external_id(settings.team_external_id)
    return team.id if team else None


@router.get("", response_model=list[MatchOut])
def list_matches(
    limit: int | None = Query(default=None, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict]:
    team_id = _primary_team_id(db)
    matches = MatchRepository(db).list_matches(team_id=team_id, limit=limit)
    return [serialize_match(m) for m in matches]


@router.get("/upcoming", response_model=list[MatchOut])
def upcoming_matches(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    team_id = _primary_team_id(db)
    if team_id is None:
        return []
    matches = MatchRepository(db).get_upcoming(team_id, limit=limit)
    return [serialize_match(m) for m in matches]


@router.get("/latest", response_model=list[MatchOut])
def latest_matches(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    team_id = _primary_team_id(db)
    if team_id is None:
        return []
    matches = MatchRepository(db).get_latest(team_id, limit=limit)
    return [serialize_match(m) for m in matches]


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)) -> dict:
    match = MatchRepository(db).get_by_id(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return serialize_match(match)
