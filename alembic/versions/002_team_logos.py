"""Store club crest URLs and last lookup time."""

import sqlalchemy as sa
from alembic import op

revision = "002_team_logos"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("teams", sa.Column("logo_url", sa.String(2048), nullable=True))
    op.add_column("teams", sa.Column("logo_checked_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("teams", "logo_checked_at")
    op.drop_column("teams", "logo_url")
