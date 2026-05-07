"""
Smoke tests — run against real URLs to verify everything works.
Requires FIRECRAWL_API_KEY in .env
"""
import pytest
from web_intel import scrape, search, extract


def test_scrape_basic():
    result = scrape("https://example.com")
    assert isinstance(result, str)
    assert len(result) > 100
    print(f"✅ scrape: {len(result)} chars")


def test_search_basic():
    results = search("Python programming", limit=3)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "url" in results[0]
    print(f"✅ search: {len(results)} results")


def test_search_with_content():
    results = search("Firecrawl web scraping", limit=2, with_content=True)
    assert isinstance(results, list)
    assert len(results) > 0
    print(f"✅ search with content: {len(results[0].get('content', ''))} chars")


def test_extract_basic():
    result = extract(
        "https://example.com",
        schema={"title": str, "description": str}
    )
    assert isinstance(result, dict)
    print(f"✅ extract: {result}")


if __name__ == "__main__":
    test_scrape_basic()
    test_search_basic()
    test_search_with_content()
    test_extract_basic()
    print("\n✅ All smoke tests passed")
