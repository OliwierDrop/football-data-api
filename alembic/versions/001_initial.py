"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-10-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("external_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_teams_external_id", "teams", ["external_id"])
    op.create_index("ix_teams_name", "teams", ["name"])

    op.create_table(
        "competitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_competitions_external_id", "competitions", ["external_id"])
    op.create_index("ix_competitions_name", "competitions", ["name"])

    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("external_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_seasons_external_id", "seasons", ["external_id"])

    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scraper_name", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("records_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_scrape_runs_scraper_name", "scrape_runs", ["scraper_name"])
    op.create_index("ix_scrape_runs_status", "scrape_runs", ["status"])

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("match_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("round", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="scheduled"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("external_id", name="uq_matches_external_id"),
    )
    op.create_index("ix_matches_external_id", "matches", ["external_id"])
    op.create_index("ix_matches_home_team_id", "matches", ["home_team_id"])
    op.create_index("ix_matches_away_team_id", "matches", ["away_team_id"])
    op.create_index("ix_matches_competition_id", "matches", ["competition_id"])
    op.create_index("ix_matches_season_id", "matches", ["season_id"])
    op.create_index("ix_matches_match_date", "matches", ["match_date"])
    op.create_index("ix_matches_status", "matches", ["status"])

    op.create_table(
        "standings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("won", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("drawn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_for", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_against", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint(
            "competition_id",
            "season_id",
            "team_id",
            name="uq_standing_competition_season_team",
        ),
    )
    op.create_index("ix_standings_competition_id", "standings", ["competition_id"])
    op.create_index("ix_standings_season_id", "standings", ["season_id"])
    op.create_index("ix_standings_team_id", "standings", ["team_id"])


def downgrade() -> None:
    op.drop_table("standings")
    op.drop_table("matches")
    op.drop_table("scrape_runs")
    op.drop_table("seasons")
    op.drop_table("competitions")
    op.drop_table("teams")
