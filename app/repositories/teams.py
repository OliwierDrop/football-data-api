from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Competition, Season, Standing, Team
from app.utils.names import clean_team_name


class TeamRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_external_id(self, external_id: str) -> Team | None:
        return self.db.scalars(select(Team).where(Team.external_id == external_id)).first()

    def get_by_name(self, name: str) -> Team | None:
        cleaned = clean_team_name(name)
        team = self.db.scalars(select(Team).where(Team.name == cleaned)).first()
        if team is not None:
            return team
        # Legacy rows may still contain the `(k)` marker
        return self.db.scalars(select(Team).where(Team.name == name)).first()

    def get_or_create(self, *, name: str, external_id: str | None = None) -> tuple[Team, bool]:
        name = clean_team_name(name)
        team = None
        if external_id:
            team = self.get_by_external_id(external_id)
        if team is None:
            team = self.get_by_name(name)
        if team is not None:
            changed = False
            if external_id and team.external_id != external_id:
                team.external_id = external_id
                changed = True
            cleaned_existing = clean_team_name(team.name)
            if team.name != cleaned_existing:
                team.name = cleaned_existing
                changed = True
            elif team.name != name:
                team.name = name
                changed = True
            return team, changed

        team = Team(name=name, external_id=external_id)
        self.db.add(team)
        self.db.flush()
        return team, True

    def list_all(self) -> list[Team]:
        return list(self.db.scalars(select(Team).order_by(Team.name)).all())


class CompetitionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self, *, name: str, external_id: str | None = None) -> tuple[Competition, bool]:
        competition = None
        if external_id:
            competition = self.db.scalars(
                select(Competition).where(Competition.external_id == external_id)
            ).first()
        if competition is None:
            competition = self.db.scalars(
                select(Competition).where(Competition.name == name)
            ).first()
        if competition is not None:
            changed = False
            if external_id and competition.external_id != external_id:
                competition.external_id = external_id
                changed = True
            if competition.name != name:
                competition.name = name
                changed = True
            return competition, changed

        competition = Competition(name=name, external_id=external_id)
        self.db.add(competition)
        self.db.flush()
        return competition, True

    def list_all(self) -> list[Competition]:
        return list(self.db.scalars(select(Competition).order_by(Competition.name)).all())


class SeasonRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self, *, name: str, external_id: str | None = None) -> tuple[Season, bool]:
        season = None
        if external_id:
            season = self.db.scalars(
                select(Season).where(Season.external_id == external_id)
            ).first()
        if season is None:
            season = self.db.scalars(select(Season).where(Season.name == name)).first()
        if season is not None:
            changed = False
            if external_id and season.external_id != external_id:
                season.external_id = external_id
                changed = True
            if season.name != name:
                season.name = name
                changed = True
            return season, changed

        season = Season(name=name, external_id=external_id)
        self.db.add(season)
        self.db.flush()
        return season, True


class StandingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_competition_season(
        self,
        *,
        competition_id: int,
        season_id: int,
    ) -> list[Standing]:
        stmt = (
            select(Standing)
            .options(joinedload(Standing.team), joinedload(Standing.competition))
            .where(
                Standing.competition_id == competition_id,
                Standing.season_id == season_id,
            )
            .order_by(Standing.position.asc())
        )
        return list(self.db.scalars(stmt).unique().all())

    def list_latest(self) -> list[Standing]:
        stmt = (
            select(Standing)
            .options(
                joinedload(Standing.team),
                joinedload(Standing.competition),
                joinedload(Standing.season),
            )
            .order_by(Standing.position.asc())
        )
        return list(self.db.scalars(stmt).unique().all())

    def serialize(self, standing: Standing) -> dict:
        return {
            "position": standing.position,
            "team": clean_team_name(standing.team.name),
            "logo_url": standing.team.logo_url,
            "played": standing.played,
            "won": standing.won,
            "drawn": standing.drawn,
            "lost": standing.lost,
            "goals_for": standing.goals_for,
            "goals_against": standing.goals_against,
            "goal_diff": standing.goals_for - standing.goals_against,
            "points": standing.points,
        }
