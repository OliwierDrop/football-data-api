from datetime import datetime, timezone

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Match
from app.utils.names import clean_team_name


def serialize_match(match: Match) -> dict:
    return {
        "id": match.id,
        "date": match.match_date,
        "home_team": clean_team_name(match.home_team.name),
        "away_team": clean_team_name(match.away_team.name),
        "home_score": match.home_score,
        "away_score": match.away_score,
        "competition": match.competition.name,
        "round": match.round,
        "status": match.status,
        "season": match.season.name if match.season else None,
    }


def _base_query() -> Select:
    return select(Match).options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
        joinedload(Match.competition),
        joinedload(Match.season),
    )


class MatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_matches(
        self,
        *,
        team_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[Match]:
        stmt = _base_query().order_by(Match.match_date.asc().nulls_last(), Match.id.asc())
        if team_id is not None:
            stmt = stmt.where(
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
            )
        if status is not None:
            stmt = stmt.where(Match.status == status)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).unique().all())

    def get_by_id(self, match_id: int) -> Match | None:
        stmt = _base_query().where(Match.id == match_id)
        return self.db.scalars(stmt).unique().first()

    def get_upcoming(self, team_id: int, *, limit: int = 20) -> list[Match]:
        now = datetime.now(timezone.utc)
        stmt = (
            _base_query()
            .where(
                and_(
                    or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
                    or_(
                        Match.status == "scheduled",
                        and_(Match.match_date.is_not(None), Match.match_date >= now),
                    ),
                    Match.home_score.is_(None),
                )
            )
            .order_by(Match.match_date.asc().nulls_last(), Match.id.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())

    def get_latest(self, team_id: int, *, limit: int = 20) -> list[Match]:
        stmt = (
            _base_query()
            .where(
                and_(
                    or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
                    Match.status == "finished",
                )
            )
            .order_by(Match.match_date.desc().nulls_last(), Match.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())

    def get_last_match(self, team_id: int) -> Match | None:
        matches = self.get_latest(team_id, limit=1)
        return matches[0] if matches else None

    def get_next_match(self, team_id: int) -> Match | None:
        matches = self.get_upcoming(team_id, limit=1)
        return matches[0] if matches else None

    def get_by_external_id(self, external_id: str) -> Match | None:
        return self.db.scalars(select(Match).where(Match.external_id == external_id)).first()
