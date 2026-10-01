from app.config import settings
from app.scraper.client import NinetyMinutClient
from app.scraper.parsers.standings import parse_standings_html
from app.scraper.types import ParsedStanding


def scrape_standings(
    client: NinetyMinutClient | None = None,
    *,
    league_path: str | None = None,
) -> list[ParsedStanding]:
    client = client or NinetyMinutClient()
    league_path = league_path or settings.league_path
    html = client.fetch_league_standings(league_path)
    return parse_standings_html(html)
