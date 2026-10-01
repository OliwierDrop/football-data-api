from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TeamBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CompetitionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SeasonBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime | None = None
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    competition: str
    round: str | None
    status: str
    season: str | None = None


class StandingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_diff: int
    points: int


class HomeOut(BaseModel):
    last_match: MatchOut | None
    next_match: MatchOut | None
    standings: list[StandingOut]


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    external_id: str | None = None


class CompetitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    external_id: str | None = None


class HealthOut(BaseModel):
    status: str
    database: str
    last_successful_sync: datetime | None = None
