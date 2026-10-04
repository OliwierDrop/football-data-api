import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup


def parse_team_logo_html(html: str, page_url: str) -> str | None:
    """Find a crest, ignoring unrelated page graphics and advertisements."""
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[tuple[int, str]] = []
    for image in soup.find_all("img", src=True):
        source = image["src"].strip()
        url = urljoin(page_url, source)
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        path = parsed.path.lower()
        label = " ".join(str(image.get(attr, "")) for attr in ("alt", "title")).lower()
        score = 0
        if re.search(r"/(?:logo|logos|herb|herby)/", path):
            score = 2
        if "herb" in label:
            score += 3
        if score:
            candidates.append((score, url))
    return max(candidates, key=lambda candidate: candidate[0])[1] if candidates else None
