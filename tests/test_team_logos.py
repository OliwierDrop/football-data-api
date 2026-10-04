from datetime import datetime, timezone
from unittest.mock import Mock

import httpx

from app.models import Team
from app.scraper.logo_sources import TEAM_LOGO_URL_FALLBACKS
from app.scraper.parsers.teams import parse_team_logo_html
from app.services.sync import SyncService


def test_logo_parser_resolves_relative_crest_and_ignores_page_logo():
    html = '<img src="/img/logo.gif"><img src="logo/club.gif"><img src="/ads/banner.gif">'
    assert parse_team_logo_html(html, "http://www.90minut.pl/skarb.php?id_klub=1") == (
        "http://www.90minut.pl/logo/club.gif"
    )


def test_logo_parser_prefers_explicit_crest():
    html = '<img src="/logo/sponsor.png"><img alt="Herb klubu" src="//cdn.example.com/club.png">'
    assert parse_team_logo_html(html, "https://www.90minut.pl/skarb.php") == (
        "https://cdn.example.com/club.png"
    )


def test_logo_parser_actual_90minut_crest_path():
    html = '<img src="http://img.90minut.pl/logo/dobazy/legia.gif" alt="Legia Warszawa">'
    assert parse_team_logo_html(html, "http://www.90minut.pl/skarb.php?id_klub=171") == (
        "http://img.90minut.pl/logo/dobazy/legia.gif"
    )


def test_logo_parser_missing_or_unsafe_image():
    assert parse_team_logo_html('<img src="/img/banner.gif">', "http://www.90minut.pl") is None
    assert parse_team_logo_html('<img alt="Herb" src="javascript:alert(1)">', "http://www.90minut.pl") is None


def test_sync_keeps_existing_logo_on_failure_and_continues():
    service = SyncService(Mock(), client=Mock())
    service.client.base_url = "http://www.90minut.pl"
    service.client.team_profile_path.return_value = "/skarb.php?id_klub=2"
    service.client.fetch_team_profile.side_effect = [httpx.ConnectError("offline"), '<img src="/logo/2.gif">']
    first = Team(name="First", external_id="1", logo_url="http://example.com/old.gif")
    second = Team(name="Second", external_id="2")
    service.teams.list_all = Mock(return_value=[first, second])
    service._start_run = Mock()
    service._finish_run = Mock(side_effect=lambda run, **kwargs: kwargs)
    result = service.sync_team_logos()
    assert first.logo_url == "http://example.com/old.gif"
    assert first.logo_checked_at is None
    assert second.logo_url == "http://www.90minut.pl/logo/2.gif"
    assert result["updated"] == 1
    assert result["status"] == "error"
    service.db.commit.assert_called_once()


def test_sync_skips_recent_checks_and_preserves_logo_when_missing():
    service = SyncService(Mock(), client=Mock())
    service.client.base_url = "http://www.90minut.pl"
    service.client.team_profile_path.return_value = "/skarb.php"
    service.client.fetch_team_profile.return_value = "<html></html>"
    recent = Team(name="Recent", external_id="1", logo_checked_at=datetime.now(timezone.utc))
    old = Team(name="Old", external_id="2", logo_url="http://example.com/old.gif")
    service.teams.list_all = Mock(return_value=[recent, old, Team(name="Unknown")])
    service._start_run = Mock()
    service._finish_run = Mock(side_effect=lambda run, **kwargs: kwargs)
    service.sync_team_logos()
    service.client.fetch_team_profile.assert_called_once()
    assert old.logo_url == "http://example.com/old.gif"
    assert old.logo_checked_at is not None


def test_reserve_logo_falls_back_to_mapped_first_team_even_after_recent_empty_check():
    service = SyncService(Mock(), client=Mock())
    service.client.base_url = "http://www.90minut.pl"
    service.client.team_profile_path.return_value = "/skarb.php"
    service.client.fetch_team_profile.side_effect = [
        "<html></html>", '<img src="http://img.90minut.pl/logo/dobazy/polonia_srodawlkp.gif">',
    ]
    team = Team(name="Polonia II Środa Wielkopolska", external_id="20229",
                logo_checked_at=datetime.now(timezone.utc))
    service.teams.list_all = Mock(return_value=[team])
    service._start_run = Mock()
    service._finish_run = Mock(side_effect=lambda run, **kwargs: kwargs)
    service.sync_team_logos()
    assert service.client.fetch_team_profile.call_args_list[1].args == ("1474", "67")
    assert team.logo_url == "http://img.90minut.pl/logo/dobazy/polonia_srodawlkp.gif"


def test_reserve_own_logo_takes_priority_over_first_team():
    service = SyncService(Mock(), client=Mock())
    service.client.base_url = "http://www.90minut.pl"
    service.client.team_profile_path.return_value = "/skarb.php"
    service.client.fetch_team_profile.return_value = '<img src="/logo/reserves.gif">'
    team = Team(name="Polonia II", external_id="20229")
    service.teams.list_all = Mock(return_value=[team])
    service._start_run = Mock()
    service._finish_run = Mock(side_effect=lambda run, **kwargs: kwargs)
    service.sync_team_logos()
    service.client.fetch_team_profile.assert_called_once()
    assert team.logo_url == "http://www.90minut.pl/logo/reserves.gif"


def test_hardcoded_logo_is_used_when_profile_has_no_crest():
    service = SyncService(Mock(), client=Mock())
    service.client.base_url = "http://www.90minut.pl"
    service.client.team_profile_path.return_value = "/skarb.php"
    service.client.fetch_team_profile.return_value = "<html></html>"
    team = Team(name="Legionistki II Warszawa", external_id="26717",
                logo_checked_at=datetime.now(timezone.utc))
    service.teams.list_all = Mock(return_value=[team])
    service._start_run = Mock()
    service._finish_run = Mock(side_effect=lambda run, **kwargs: kwargs)
    result = service.sync_team_logos()
    assert team.logo_url == TEAM_LOGO_URL_FALLBACKS["26717"]
    assert result["updated"] == 1
    service.client.fetch_team_profile.assert_called_once()
    assert service.sync_team_logos()["updated"] == 0


def test_profile_logo_takes_priority_over_hardcoded_url():
    service = SyncService(Mock(), client=Mock())
    service.client.base_url = "http://www.90minut.pl"
    service.client.team_profile_path.return_value = "/skarb.php"
    service.client.fetch_team_profile.return_value = '<img src="/logo/legionistki.gif">'
    team = Team(name="Legionistki II Warszawa", external_id="26717",
                logo_url=TEAM_LOGO_URL_FALLBACKS["26717"])
    service.teams.list_all = Mock(return_value=[team])
    service._start_run = Mock()
    service._finish_run = Mock(side_effect=lambda run, **kwargs: kwargs)
    service.sync_team_logos()
    assert team.logo_url == "http://www.90minut.pl/logo/legionistki.gif"
