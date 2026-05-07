"""
llm.py — provider-agnostic LLM client.
Reads WEB_INTEL_PROVIDER env var to route to OpenAI / NVIDIA NIM / Anthropic.
"""
from openai import OpenAI
from ..config import PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client for the configured provider."""
    if PROVIDER == "nvidia":
        return OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL or "https://integrate.api.nvidia.com/v1"
        )
    elif PROVIDER == "anthropic":
        # Anthropic has OpenAI-compatible endpoint
        return OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL or "https://api.anthropic.com/v1"
        )
    else:
        # Default: OpenAI
        kwargs = {"api_key": LLM_API_KEY}
        if LLM_BASE_URL:
            kwargs["base_url"] = LLM_BASE_URL
        return OpenAI(**kwargs)


def call_llm(prompt: str, system: str = "You are a helpful assistant.", url: str = "") -> str:
    """Simple single-turn LLM call. Logs token usage to popup if url provided."""
    from ..popup import log_usage
    client = get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    usage = response.usage
    if usage and url:
        log_usage(url, usage.prompt_tokens, usage.completion_tokens)
    return response.choices[0].message.content or ""
