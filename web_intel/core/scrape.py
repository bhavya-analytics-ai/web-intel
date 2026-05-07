"""
scrape.py — fetch a single URL, return clean markdown content.
Firecrawl handles JS, proxies, rate limits under the hood.
"""
from firecrawl import V1FirecrawlApp as FirecrawlApp
from ..config import FIRECRAWL_URL, FIRECRAWL_API_KEY


def scrape(url: str, formats: list = None) -> str:
    """
    Fetch a single URL and return clean markdown.

    Args:
        url: The URL to scrape
        formats: List of formats to return (default: ["markdown"])

    Returns:
        Markdown string of page content
    """
    if formats is None:
        formats = ["markdown"]

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY, api_url=FIRECRAWL_URL)
    result = app.scrape_url(url, formats=formats)

    if hasattr(result, "markdown"):
        return result.markdown or ""
    if isinstance(result, dict):
        return result.get("markdown", "")
    return str(result)
