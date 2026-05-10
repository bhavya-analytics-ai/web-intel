"""
extract.py — structured data extraction from one or many URLs.
Uses Firecrawl's extract endpoint + LLM fallback to pull exact fields from any page.
"""
import json
from openai import OpenAI
from firecrawl import V1FirecrawlApp as FirecrawlApp
from ..config import FIRECRAWL_URL, FIRECRAWL_API_KEY, PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from .scrape import scrape
from .output import save_json


def _call_llm(prompt: str) -> str:
    """LLM fallback for extraction — NIM or OpenAI."""
    if PROVIDER == "nvidia":
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL or "https://integrate.api.nvidia.com/v1")
    else:
        client = OpenAI(api_key=LLM_API_KEY)
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return resp.choices[0].message.content or ""


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
    except Exception:
        return {k: None for k in schema}

    if not content:
        return {k: None for k in schema}

    fields = list(schema.keys())
    llm_prompt = f"""Extract the following fields from this web page content.
Return ONLY valid JSON with these exact keys: {fields}
If a field is not found, use null.

Content:
{content[:8000]}

Return JSON:"""

    try:
        raw = _call_llm(llm_prompt)
    except Exception:
        return {k: None for k in schema}

    try:
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        result = json.loads(raw)
        save_json(url, result)
        return result
    except Exception:
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
