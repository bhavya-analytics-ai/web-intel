# Project Context — web-intel + Next Steps

## What we built
**web-intel** — self-hosted scraping + structured extraction library
- Repo: https://github.com/bhavya-analytics-ai/web-intel
- Location: `~/Desktop/github_skills/web_intel/`
- Venv: `source scraping/bin/activate`

### Stack
- **Firecrawl** self-hosted on Hetzner CX23 (`46.224.203.138:3002`) — €5.59/month flat, unlimited scrapes
- **Firewall** applied — port 3002 locked to Mac IP `47.230.39.48/32` only
- **5 functions:** `scrape`, `search`, `crawl`, `extract`, `extract_many`
- **MCP server** — mount in TRUMAN via `python -m web_intel.server`
- **Live stats popup** — spawns on first `extract()` call, shows tokens/cost/URL. Open manually: `python open_popup.py`
- **Provider-agnostic LLM** — env vars route to OpenAI/NVIDIA NIM/Anthropic

### .env (at `~/Desktop/github_skills/web_intel/.env`)
```
FIRECRAWL_API_KEY=localonlykey
FIRECRAWL_URL=http://46.224.203.138:3002
WEB_INTEL_PROVIDER=openai
WEB_INTEL_API_KEY=<openai key — user has it>
WEB_INTEL_MODEL=gpt-4o-mini
```

### Hetzner server
- IP: `46.224.203.138`
- SSH: `ssh root@46.224.203.138` (password via Adam's email)
- Firecrawl running: `cd ~/firecrawl && docker compose up -d`
- Auto-restarts on reboot: `docker update --restart=always` already applied

---

## Pending integrations

### 1. Lead Enrichment (TOMORROW — highest priority)
- Script: `~/Desktop/Lead_Scraping/enrich_top100.py`
- Currently uses **Tavily** for search + **regex** for extraction
- Plan: replace with `web_intel.search` + `web_intel.extract`
- Why: full page content instead of snippets, LLM extraction instead of regex → 80%+ hit rate vs current ~40%
- Schema to extract: `{"phone": str, "email": str, "owner_name": str, "address": str}`

### 2. TRUMAN integration
- Add to `~/Desktop/friday/truman/tools/mcp_config.py`:
```python
"web_intel": {
    "command": "python",
    "args": ["-m", "web_intel.server"],
    "env": {
        "FIRECRAWL_API_KEY": "localonlykey",
        "FIRECRAWL_URL": "http://46.224.203.138:3002",
        "WEB_INTEL_PROVIDER": "nvidia",
        "WEB_INTEL_API_KEY": "<nvidia nim key>",
        "WEB_INTEL_MODEL": "meta/llama-3.3-70b-instruct",
        "WEB_INTEL_BASE_URL": "https://integrate.api.nvidia.com/v1"
    }
}
```
- TRUMAN also has a broken tool routing issue (separate audit at `~/Desktop/AgentResearch/AgentResearch/System Design/TRUMAN_AUDIT.md`)

### 3. Local Document Intelligence (future project)
- User has merchant folders with PDFs, bank statements, Plaid reports, images
- Goal: agent watches folders, indexes everything, answers questions instantly, fills Excel templates
- Stack needed: file watcher + Azure Doc Intelligence (already have) + vector DB + LLM
- This is a separate project from web-intel

---

## Other context
- User's GitHub: `bhavya-analytics-ai`
- SEACAP is on Railway — lead pipeline project
- TRUMAN is at `~/Desktop/friday/truman` — personal AI assistant, LangGraph, Phase 15
- AgentResearch notes at `~/Desktop/AgentResearch/AgentResearch/`
- User style: direct, no fluff, discuss before making any changes
