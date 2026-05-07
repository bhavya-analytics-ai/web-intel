"""
web_intel — reusable web scraping + structured extraction module.
Plug into any Python project or mount as an MCP server.

Usage:
    from web_intel import scrape, search, crawl, extract, extract_many
"""
from .core.scrape import scrape
from .core.crawl import crawl
from .core.search import search
from .core.extract import extract, extract_many

__all__ = ["scrape", "crawl", "search", "extract", "extract_many"]
