import logging
from urllib.parse import urlencode

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class NinetyMinutClient:
    """HTTP client for 90minut.pl pages."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        user_agent: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.scraper_base_url).rstrip("/")
        self.timeout = timeout or settings.scraper_timeout_seconds
        self.user_agent = user_agent or settings.scraper_user_agent

    def fetch(self, path: str) -> str:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        logger.info("Fetching %s", url)
        with httpx.Client(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            # 90minut.pl serves iso-8859-2; httpx may mis-detect encoding
            encoding = response.charset_encoding or "iso-8859-2"
            try:
                return response.content.decode(encoding)
            except UnicodeDecodeError:
                return response.content.decode("iso-8859-2", errors="replace")

    def fetch_team_matches(self, team_id: str, season_id: str) -> str:
        return self.fetch(f"/mecze_druzyna.php?id={team_id}&id_sezon={season_id}")

    def fetch_league_standings(self, league_path: str) -> str:
        return self.fetch(league_path)

    def team_profile_path(self, team_id: str, season_id: str) -> str:
        return "/skarb.php?" + urlencode({"id_klub": team_id, "id_sezon": season_id})

    def fetch_team_profile(self, team_id: str, season_id: str) -> str:
        return self.fetch(self.team_profile_path(team_id, season_id))
