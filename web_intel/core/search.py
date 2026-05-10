"""
search.py — web search + optionally fetch full content of results.
"""
from firecrawl import V1FirecrawlApp as FirecrawlApp
from ..config import FIRECRAWL_URL, FIRECRAWL_API_KEY
from .output import save_json


def search(query: str, limit: int = 5, with_content: bool = False) -> list[dict]:
    """
    Search the web and return results.

    Args:
        query: Search query string
        limit: Number of results to return
        with_content: If True, fetch full page content for each result

    Returns:
        List of dicts with {url, title, content}
    """
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY, api_url=FIRECRAWL_URL)

    from firecrawl import V1ScrapeOptions as ScrapeOptions
    scrape_options = ScrapeOptions(formats=["markdown"]) if with_content else None
    kwargs = {"limit": limit}
    if scrape_options:
        kwargs["scrape_options"] = scrape_options
    result = app.search(query, **kwargs)

    results = []
    data = result.data if hasattr(result, "data") else result.get("data", [])
    for item in data:
        if isinstance(item, dict):
            results.append({
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "content": item.get("markdown", item.get("description", ""))
            })
        else:
            results.append({
                "url": getattr(item, "url", ""),
                "title": getattr(item, "title", ""),
                "content": getattr(item, "markdown", getattr(item, "description", ""))
            })
    save_json(query, results)
    return results
