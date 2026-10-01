from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.repositories.teams import CompetitionRepository, TeamRepository
from app.schemas import CompetitionOut, TeamOut
from app.utils.names import clean_team_name

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/team", response_model=TeamOut | None)
def get_team(db: Session = Depends(get_db)) -> TeamOut | None:
    team = TeamRepository(db).get_by_external_id(settings.team_external_id)
    if team is None:
        return None
    return TeamOut(
        id=team.id,
        name=clean_team_name(team.name),
        external_id=team.external_id,
    )


@router.get("/competitions", response_model=list[CompetitionOut])
def list_competitions(db: Session = Depends(get_db)) -> list[CompetitionOut]:
    competitions = CompetitionRepository(db).list_all()
    return [CompetitionOut.model_validate(c) for c in competitions]
