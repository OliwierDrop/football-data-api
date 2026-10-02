import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from app.scraper.types import ParsedMatch

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?$")
SCORE_RE = re.compile(r"^(\d+)\s*[-–:]\s*(\d+)$")
TEAM_ID_RE = re.compile(r"id=(\d+)")
# 90minut.pl publishes kick-off times in Poland local time (CET/CEST).
WARSAW = ZoneInfo("Europe/Warsaw")


def _text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def _extract_team(cell) -> tuple[str, str | None]:
    link = cell.find("a", href=True) if cell else None
    if link:
        name = _text(link)
        match = TEAM_ID_RE.search(link["href"])
        return name, match.group(1) if match else None
    return _text(cell), None


def _parse_date(raw: str) -> datetime | None:
    """Parse 90minut wall-clock time as Europe/Warsaw and return UTC."""
    raw = raw.strip()
    if not raw:
        return None
    match = DATE_RE.match(raw)
    if not match:
        return None
    date_part, time_part = match.group(1), match.group(2)
    if time_part:
        dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
    else:
        dt = datetime.strptime(date_part, "%Y-%m-%d")
    return dt.replace(tzinfo=WARSAW).astimezone(timezone.utc)


def _parse_score(raw: str) -> tuple[int | None, int | None, str]:
    raw = raw.strip()
    if not raw or raw == "-":
        return None, None, "scheduled"
    # walkover / postponed markers occasionally appear as e.g. "3-0 (wo)"
    cleaned = re.sub(r"\s*\([^)]*\)\s*", "", raw).strip()
    match = SCORE_RE.match(cleaned)
    if not match:
        return None, None, "scheduled"
    return int(match.group(1)), int(match.group(2)), "finished"


def _split_competition_round(raw: str, default_competition: str) -> tuple[str, str | None]:
    raw = raw.strip()
    if not raw:
        return default_competition, None
    if "," in raw:
        competition, round_part = raw.split(",", 1)
        return competition.strip(), round_part.strip() or None
    lower = raw.lower()
    if lower.startswith("kolejka"):
        return default_competition, raw
    if "finał" in lower or "final" in lower or lower.startswith("pokr") or "puchar" in lower:
        return "Orlen Puchar Polski kobiet", raw
    return raw, None


def parse_matches_html(
    html: str,
    *,
    default_competition: str = "II liga kobiet",
) -> list[ParsedMatch]:
    soup = BeautifulSoup(html, "html.parser")
    matches: list[ParsedMatch] = []

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        date_raw = _text(cells[0])
        competition_raw = _text(cells[1])
        home_name, home_ext = _extract_team(cells[2])
        score_raw = _text(cells[3])
        away_name, away_ext = _extract_team(cells[4])

        # Skip header / summary rows
        if competition_raw.lower() in {"rozgrywki", ""} and not home_name:
            continue
        if not home_name or not away_name:
            continue
        if competition_raw.lower() in {"rozgrywki"}:
            continue

        competition, round_name = _split_competition_round(competition_raw, default_competition)
        home_score, away_score, status = _parse_score(score_raw)
        match_date = _parse_date(date_raw)

        matches.append(
            ParsedMatch(
                date=match_date,
                competition_name=competition,
                round=round_name,
                home_team_name=home_name,
                away_team_name=away_name,
                home_team_external_id=home_ext,
                away_team_external_id=away_ext,
                home_score=home_score,
                away_score=away_score,
                status=status,
            )
        )

    return matches
