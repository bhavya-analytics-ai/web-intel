"""
config.py — loads env vars, routes to correct LLM provider and Firecrawl URL.
Each system sets its own .env — same library, different brains.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Firecrawl — self-hosted (Hetzner) or cloud
FIRECRAWL_URL = os.getenv("FIRECRAWL_URL", "https://api.firecrawl.dev")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

# LLM provider routing
PROVIDER = os.getenv("WEB_INTEL_PROVIDER", "openai")  # openai | nvidia | anthropic
LLM_API_KEY = os.getenv("WEB_INTEL_API_KEY", "")
LLM_MODEL = os.getenv("WEB_INTEL_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.getenv("WEB_INTEL_BASE_URL", None)  # needed for NIM
