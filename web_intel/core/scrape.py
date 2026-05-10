"""
scrape.py — fetch a single URL, return clean markdown content.
Firecrawl handles JS, proxies, rate limits under the hood.
Auto-injects cookies from cookies.json for auth-walled sites.
Auto-saves output to outputs/ folder.
"""
import os
import json
from urllib.parse import urlparse
from firecrawl import V1FirecrawlApp as FirecrawlApp
from ..config import FIRECRAWL_URL, FIRECRAWL_API_KEY
from .output import save_md

_COOKIES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "cookies.json")


def _load_cookies(url: str) -> dict:
    """Load cookies for the domain from cookies.json if it exists."""
    try:
        if not os.path.exists(_COOKIES_PATH):
            return {}
        with open(_COOKIES_PATH, "r") as f:
            cookie_store = json.load(f)
        domain = urlparse(url).netloc.lstrip("www.")
        for key in cookie_store:
            if key in domain:
                return {"Cookie": cookie_store[key]}
    except Exception:
        pass
    return {}


def scrape(url: str, formats: list = None) -> str:
    """
    Fetch a single URL and return clean markdown.
    Auto-injects cookies for known auth-walled domains.
    Auto-saves result to outputs/ folder.

    Args:
        url: The URL to scrape
        formats: List of formats to return (default: ["markdown"])

    Returns:
        Markdown string of page content
    """
    if formats is None:
        formats = ["markdown"]

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY, api_url=FIRECRAWL_URL)
    headers = _load_cookies(url)

    kwargs = {"formats": formats}
    if headers:
        kwargs["headers"] = headers

    result = app.scrape_url(url, **kwargs)

    if hasattr(result, "markdown"):
        content = result.markdown or ""
    elif isinstance(result, dict):
        content = result.get("markdown", "")
    else:
        content = str(result)

    save_md(url, content)
    return content
