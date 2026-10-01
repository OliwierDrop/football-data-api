import re

_WOMEN_MARKER = re.compile(r"\s*\(k\)\s*$", re.IGNORECASE)


def clean_team_name(name: str) -> str:
    """Remove 90minut.pl women's team marker `(k)` from display names."""
    return _WOMEN_MARKER.sub("", name or "").strip()
