from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.repositories.matches import MatchRepository, serialize_match
from app.repositories.teams import StandingRepository, TeamRepository
from app.schemas import HomeOut, MatchOut, StandingOut

router = APIRouter(prefix="/api", tags=["home"])


@router.get("/home", response_model=HomeOut)
def home(db: Session = Depends(get_db)) -> HomeOut:
    team = TeamRepository(db).get_by_external_id(settings.team_external_id)
    matches_repo = MatchRepository(db)
    standings_repo = StandingRepository(db)

    last_match = None
    next_match = None
    standings: list[StandingOut] = []

    if team is not None:
        last = matches_repo.get_last_match(team.id)
        nxt = matches_repo.get_next_match(team.id)
        last_match = MatchOut(**serialize_match(last)) if last else None
        next_match = MatchOut(**serialize_match(nxt)) if nxt else None

        all_standings = standings_repo.list_latest()
        primary_rows = [s for s in all_standings if s.team_id == team.id]
        if primary_rows:
            competition_id = primary_rows[0].competition_id
            season_id = primary_rows[0].season_id
            filtered = [
                s
                for s in all_standings
                if s.competition_id == competition_id and s.season_id == season_id
            ]
            standings = [StandingOut(**standings_repo.serialize(s)) for s in filtered]

    return HomeOut(last_match=last_match, next_match=next_match, standings=standings)
