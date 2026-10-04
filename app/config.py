from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://football:football_dev_secret@postgres:5432/football"

    team_external_id: str = "23495"
    team_name: str = "Słupczanka Słupca"
    season_external_id: str = "109"
    season_name: str = "2026/27"
    league_path: str = "/liga/1/liga14872.html"
    league_name: str = "II liga kobiet, grupa: północna"

    sync_interval_minutes: int = 30
    scraper_timeout_seconds: int = 30
    scraper_user_agent: str = "FootballDataAPI/1.0"
    scraper_base_url: str = "http://www.90minut.pl"
    scrape_team_logos: bool = True

    api_cors_origins: str = "*"
    run_scheduler: bool = True

    @property
    def cors_origins(self) -> list[str]:
        if self.api_cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
