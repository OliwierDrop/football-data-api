from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo("Europe/Warsaw")


@dataclass
class ParsedMatch:
    date: datetime | None
    competition_name: str
    round: str | None
    home_team_name: str
    away_team_name: str
    home_team_external_id: str | None
    away_team_external_id: str | None
    home_score: int | None
    away_score: int | None
    status: str

    @property
    def external_id(self) -> str:
        # Use Poland calendar date so IDs stay stable across UTC conversion.
        if self.date is not None:
            date_part = self.date.astimezone(WARSAW).strftime("%Y-%m-%d")
        else:
            date_part = "nodate"
        round_part = (self.round or "noround").replace(" ", "_")
        return (
            f"{date_part}|{self.competition_name}|{round_part}|"
            f"{self.home_team_name}|{self.away_team_name}"
        )


@dataclass
class ParsedStanding:
    position: int
    team_name: str
    team_external_id: str | None
    played: int
    points: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
