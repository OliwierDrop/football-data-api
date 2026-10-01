import re

from bs4 import BeautifulSoup

from app.scraper.types import ParsedStanding

TEAM_ID_RE = re.compile(r"id_klub=(\d+)")
POSITION_RE = re.compile(r"^(\d+)\.?$")
GOALS_RE = re.compile(r"^(\d+)\s*[-–:]\s*(\d+)$")


def _text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def parse_standings_html(html: str) -> list[ParsedStanding]:
    soup = BeautifulSoup(html, "html.parser")
    standings: list[ParsedStanding] = []

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 8:
            continue

        position_raw = _text(cells[0]).rstrip(".")
        if not POSITION_RE.match(position_raw):
            continue

        team_cell = cells[1]
        link = team_cell.find("a", href=True)
        team_name = _text(link) if link else _text(team_cell)
        if not team_name:
            continue

        team_external_id = None
        if link:
            match = TEAM_ID_RE.search(link["href"])
            if match:
                team_external_id = match.group(1)

        try:
            played = int(_text(cells[2]))
            points = int(_text(cells[3]))
            won = int(_text(cells[4]))
            drawn = int(_text(cells[5]))
            lost = int(_text(cells[6]))
        except ValueError:
            continue

        goals_raw = _text(cells[7])
        goals_match = GOALS_RE.match(goals_raw)
        if not goals_match:
            continue

        standings.append(
            ParsedStanding(
                position=int(position_raw),
                team_name=team_name,
                team_external_id=team_external_id,
                played=played,
                points=points,
                won=won,
                drawn=drawn,
                lost=lost,
                goals_for=int(goals_match.group(1)),
                goals_against=int(goals_match.group(2)),
            )
        )

    return standings
