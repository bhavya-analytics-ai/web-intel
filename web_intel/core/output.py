"""
output.py — auto-save every web_intel result to outputs/ folder.
Called internally by scrape, search, extract, crawl.
Zero config — always on.
"""
import os
import json
import re
from datetime import datetime


OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")


def _ensure_dir():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)


def _slug(url_or_query: str) -> str:
    """Turn a URL or query into a safe filename slug."""
    slug = re.sub(r"https?://", "", url_or_query)
    slug = re.sub(r"[^\w\-]", "_", slug)
    return slug[:60]


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_md(url: str, content: str) -> str:
    """Save markdown content. Returns saved filepath."""
    _ensure_dir()
    filename = f"{_timestamp()}_{_slug(url)}.md"
    filepath = os.path.join(OUTPUTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Scraped: {url}\n\n")
        f.write(f"_Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
        f.write("---\n\n")
        f.write(content or "")
    return filepath


def save_json(label: str, data) -> str:
    """Save structured JSON data. Returns saved filepath."""
    _ensure_dir()
    filename = f"{_timestamp()}_{_slug(label)}.json"
    filepath = os.path.join(OUTPUTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath
