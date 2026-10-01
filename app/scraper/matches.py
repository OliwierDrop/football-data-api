from app.config import settings
from app.scraper.client import NinetyMinutClient
from app.scraper.parsers.matches import parse_matches_html
from app.scraper.types import ParsedMatch


def scrape_team_matches(
    client: NinetyMinutClient | None = None,
    *,
    team_id: str | None = None,
    season_id: str | None = None,
    default_competition: str | None = None,
) -> list[ParsedMatch]:
    client = client or NinetyMinutClient()
    team_id = team_id or settings.team_external_id
    season_id = season_id or settings.season_external_id
    default_competition = default_competition or settings.league_name.split(",")[0].strip()

    html = client.fetch_team_matches(team_id, season_id)
    return parse_matches_html(html, default_competition=default_competition)
