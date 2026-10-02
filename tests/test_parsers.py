from datetime import datetime, timezone

from app.scraper.parsers.matches import parse_matches_html
from app.scraper.parsers.standings import parse_standings_html

SAMPLE_MATCHES = """
<html><body>
<table>
<tr bgcolor="#B81B1B"><td>data</td><td>rozgrywki</td><td>gospodarze</td><td>wynik</td><td>goście</td></tr>
<tr bgcolor="#F5F5F5">
  <td><nobr>2026-08-22 12:30</nobr></td>
  <td>Kolejka 1</td>
  <td><a href="/mecze_druzyna.php?id=27783&id_sezon=109">KKP Warszawa (k)</a></td>
  <td><b>3-1</b></td>
  <td><b><u>Słupczanka Słupca (k)</u></b></td>
</tr>
<tr bgcolor="#DFDFDF">
  <td><nobr>2026-10-04 15:00</nobr></td>
  <td>Kolejka 6</td>
  <td><b><u>Słupczanka Słupca (k)</u></b></td>
  <td><b>-</b></td>
  <td><a href="/mecze_druzyna.php?id=25949&id_sezon=109">Wisła Płock (k)</a></td>
</tr>
</table>
</body></html>
"""

SAMPLE_STANDINGS = """
<html><body>
<table>
<tr bgcolor="#B81B1B">
  <td></td><td>Nazwa</td><td>M.</td><td>Pkt.</td><td>Z.</td><td>R.</td><td>P.</td><td>Bramki</td>
</tr>
<tr>
  <td><b>5.</b></td>
  <td><a href="/skarb.php?id_klub=23495&id_sezon=109">Słupczanka Słupca</a></td>
  <td>5</td><td><b>7</b></td><td>2</td><td>1</td><td>2</td><td>12-9</td>
</tr>
</table>
</body></html>
"""


def test_parse_matches():
    matches = parse_matches_html(SAMPLE_MATCHES, default_competition="II liga kobiet")
    assert len(matches) == 2
    assert matches[0].home_team_name == "KKP Warszawa (k)"
    assert matches[0].away_team_name == "Słupczanka Słupca (k)"
    assert matches[0].home_score == 3
    assert matches[0].away_score == 1
    assert matches[0].status == "finished"
    assert matches[0].round == "Kolejka 1"
    # 12:30 Warsaw (CEST, UTC+2) → 10:30 UTC
    assert matches[0].date == datetime(2026, 8, 22, 10, 30, tzinfo=timezone.utc)
    assert matches[1].status == "scheduled"
    assert matches[1].home_score is None
    # 15:00 Warsaw (CEST, UTC+2) → 13:00 UTC
    assert matches[1].date == datetime(2026, 10, 4, 13, 0, tzinfo=timezone.utc)


def test_parse_standings():
    standings = parse_standings_html(SAMPLE_STANDINGS)
    assert len(standings) == 1
    row = standings[0]
    assert row.position == 5
    assert row.team_external_id == "23495"
    assert row.points == 7
    assert row.goals_for == 12
    assert row.goals_against == 9
