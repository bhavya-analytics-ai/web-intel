"""
crawl.py — crawl an entire website, return list of pages.
"""
from firecrawl import V1FirecrawlApp as FirecrawlApp
from ..config import FIRECRAWL_URL, FIRECRAWL_API_KEY
from .output import save_json


def crawl(url: str, max_pages: int = 50) -> list[dict]:
    """
    Crawl a website up to max_pages deep.

    Args:
        url: Root URL to crawl
        max_pages: Maximum number of pages to crawl

    Returns:
        List of dicts with {url, markdown} per page
    """
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY, api_url=FIRECRAWL_URL)
    result = app.crawl_url(url, limit=max_pages, scrape_options={"formats": ["markdown"]})

    pages = []
    data = result.data if hasattr(result, "data") else result.get("data", [])
    for page in data:
        if hasattr(page, "markdown"):
            pages.append({"url": getattr(page, "url", ""), "markdown": page.markdown or ""})
        elif isinstance(page, dict):
            pages.append({"url": page.get("url", ""), "markdown": page.get("markdown", "")})
    save_json(url, pages)
    return pages
