import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Match, ScrapeRun, Standing
from app.repositories.matches import MatchRepository
from app.repositories.teams import (
    CompetitionRepository,
    SeasonRepository,
    StandingRepository,
    TeamRepository,
)
from app.scraper.client import NinetyMinutClient
from app.scraper.matches import scrape_team_matches
from app.scraper.standings import scrape_standings
from app.scraper.types import ParsedMatch, ParsedStanding

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self, db: Session, client: NinetyMinutClient | None = None) -> None:
        self.db = db
        self.client = client or NinetyMinutClient()
        self.teams = TeamRepository(db)
        self.competitions = CompetitionRepository(db)
        self.seasons = SeasonRepository(db)
        self.matches = MatchRepository(db)
        self.standings = StandingRepository(db)

    def sync_all(self) -> dict:
        matches_result = self.sync_matches()
        standings_result = self.sync_standings()
        return {"matches": matches_result, "standings": standings_result}

    def sync_matches(self) -> dict:
        run = self._start_run("matches")
        created = updated = 0
        try:
            parsed = scrape_team_matches(self.client)
            season, _ = self.seasons.get_or_create(
                name=settings.season_name,
                external_id=settings.season_external_id,
            )
            # Ensure primary team exists
            self.teams.get_or_create(
                name=settings.team_name,
                external_id=settings.team_external_id,
            )

            for item in parsed:
                was_created = self._upsert_match(item, season.id)
                if was_created:
                    created += 1
                else:
                    updated += 1

            self.db.commit()
            return self._finish_run(
                run,
                status="success",
                found=len(parsed),
                created=created,
                updated=updated,
            )
        except Exception as exc:
            logger.exception("Match sync failed")
            self.db.rollback()
            return self._finish_run(
                run,
                status="error",
                found=0,
                created=created,
                updated=updated,
                error=str(exc),
            )

    def sync_standings(self) -> dict:
        run = self._start_run("standings")
        created = updated = 0
        try:
            parsed = scrape_standings(self.client)
            season, _ = self.seasons.get_or_create(
                name=settings.season_name,
                external_id=settings.season_external_id,
            )
            competition, _ = self.competitions.get_or_create(
                name=settings.league_name,
                external_id=self._league_external_id(),
            )

            for item in parsed:
                was_created = self._upsert_standing(item, competition.id, season.id)
                if was_created:
                    created += 1
                else:
                    updated += 1

            self.db.commit()
            return self._finish_run(
                run,
                status="success",
                found=len(parsed),
                created=created,
                updated=updated,
            )
        except Exception as exc:
            logger.exception("Standings sync failed")
            self.db.rollback()
            return self._finish_run(
                run,
                status="error",
                found=0,
                created=created,
                updated=updated,
                error=str(exc),
            )

    def _upsert_match(self, item: ParsedMatch, season_id: int) -> bool:
        home, _ = self.teams.get_or_create(
            name=item.home_team_name,
            external_id=item.home_team_external_id,
        )
        away, _ = self.teams.get_or_create(
            name=item.away_team_name,
            external_id=item.away_team_external_id,
        )
        competition, _ = self.competitions.get_or_create(name=item.competition_name)

        existing = self.matches.get_by_external_id(item.external_id)
        if existing is None:
            match = Match(
                external_id=item.external_id,
                home_team_id=home.id,
                away_team_id=away.id,
                competition_id=competition.id,
                season_id=season_id,
                match_date=item.date,
                home_score=item.home_score,
                away_score=item.away_score,
                round=item.round,
                status=item.status,
            )
            self.db.add(match)
            self.db.flush()
            return True

        existing.home_team_id = home.id
        existing.away_team_id = away.id
        existing.competition_id = competition.id
        existing.season_id = season_id
        existing.match_date = item.date
        existing.home_score = item.home_score
        existing.away_score = item.away_score
        existing.round = item.round
        existing.status = item.status
        self.db.flush()
        return False

    def _upsert_standing(
        self,
        item: ParsedStanding,
        competition_id: int,
        season_id: int,
    ) -> bool:
        team_name = item.team_name
        if item.team_external_id == settings.team_external_id:
            team_name = settings.team_name

        team, _ = self.teams.get_or_create(
            name=team_name,
            external_id=item.team_external_id,
        )

        existing = self.db.scalars(
            select(Standing).where(
                Standing.competition_id == competition_id,
                Standing.season_id == season_id,
                Standing.team_id == team.id,
            )
        ).first()

        if existing is None:
            standing = Standing(
                competition_id=competition_id,
                season_id=season_id,
                team_id=team.id,
                position=item.position,
                played=item.played,
                won=item.won,
                drawn=item.drawn,
                lost=item.lost,
                goals_for=item.goals_for,
                goals_against=item.goals_against,
                points=item.points,
            )
            self.db.add(standing)
            self.db.flush()
            return True

        existing.position = item.position
        existing.played = item.played
        existing.won = item.won
        existing.drawn = item.drawn
        existing.lost = item.lost
        existing.goals_for = item.goals_for
        existing.goals_against = item.goals_against
        existing.points = item.points
        self.db.flush()
        return False

    def _league_external_id(self) -> str | None:
        # e.g. /liga/1/liga14872.html -> 14872
        path = settings.league_path
        digits = "".join(ch for ch in path.split("/")[-1] if ch.isdigit())
        return digits or None

    def _start_run(self, scraper_name: str) -> ScrapeRun:
        run = ScrapeRun(
            scraper_name=scraper_name,
            started_at=datetime.now(timezone.utc),
            status="running",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def _finish_run(
        self,
        run: ScrapeRun,
        *,
        status: str,
        found: int,
        created: int,
        updated: int,
        error: str | None = None,
    ) -> dict:
        run.finished_at = datetime.now(timezone.utc)
        run.status = status
        run.records_found = found
        run.records_created = created
        run.records_updated = updated
        run.error_message = error
        self.db.add(run)
        self.db.commit()
        return {
            "scraper_name": run.scraper_name,
            "status": status,
            "records_found": found,
            "records_created": created,
            "records_updated": updated,
            "error_message": error,
        }
