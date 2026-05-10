"""
extract.py — structured data extraction from one or many URLs.
Uses Firecrawl's extract endpoint + LLM to pull exact fields from any page.
"""
import json
from firecrawl import V1FirecrawlApp as FirecrawlApp
from ..config import FIRECRAWL_URL, FIRECRAWL_API_KEY
from .llm import call_llm
from .scrape import scrape
from .output import save_json


def extract(url: str, schema: dict, prompt: str = None) -> dict:
    """
    Extract structured data from a single URL.

    Args:
        url: The URL to extract from
        schema: Dict of {field_name: type} e.g. {"company_name": str, "ceo": str}
        prompt: Optional custom extraction prompt

    Returns:
        Dict matching the schema with extracted values
    """
    # Try Firecrawl's native extract first
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY, api_url=FIRECRAWL_URL)
        schema_prompt = prompt or f"Extract the following fields: {list(schema.keys())}"
        result = app.extract([url], prompt=schema_prompt)
        if result and hasattr(result, "data") and result.data:
            return result.data[0] if isinstance(result.data, list) else result.data
        if isinstance(result, dict) and result.get("data"):
            return result["data"][0] if isinstance(result["data"], list) else result["data"]
    except Exception:
        pass

    # Fallback: scrape + LLM extraction
    try:
        content = scrape(url)
    except Exception as e:
        from ..popup import log_error
        log_error(url, "scrape failed", str(e))
        return {k: None for k in schema}

    if not content:
        from ..popup import log_error
        log_error(url, "scrape returned empty content", f"URL: {url}")
        return {k: None for k in schema}

    fields = list(schema.keys())
    llm_prompt = f"""Extract the following fields from this web page content.
Return ONLY valid JSON with these exact keys: {fields}
If a field is not found, use null.

Content:
{content[:8000]}

Return JSON:"""

    try:
        raw = call_llm(llm_prompt, url=url)
    except Exception as e:
        from ..popup import log_error
        log_error(url, "LLM call failed", str(e))
        return {k: None for k in schema}

    # Parse JSON from response
    try:
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        result = json.loads(raw)
        save_json(url, result)
        return result
    except Exception as e:
        from ..popup import log_error
        log_error(url, "JSON parse failed", f"Raw response: {raw[:200]}")
        return {k: None for k in schema}


def extract_many(urls: list[str], schema: dict, prompt: str = None) -> list[dict]:
    """
    Batch extract structured data from multiple URLs.

    Args:
        urls: List of URLs to extract from
        schema: Dict of {field_name: type}
        prompt: Optional custom extraction prompt

    Returns:
        List of dicts, one per URL
    """
    # Try Firecrawl batch extract
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY, api_url=FIRECRAWL_URL)
        schema_prompt = prompt or f"Extract the following fields: {list(schema.keys())}"
        result = app.extract(urls, prompt=schema_prompt)
        if result and hasattr(result, "data"):
            return result.data if isinstance(result.data, list) else [result.data]
        if isinstance(result, dict) and result.get("data"):
            data = result["data"]
            return data if isinstance(data, list) else [data]
    except Exception:
        pass

    # Fallback: extract one by one
    return [extract(url, schema, prompt) for url in urls]
