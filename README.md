# ⚡ web-intel

> Scrape anything. Extract everything. Pay nobody.

Most devs pay per scrape. Every API call bleeds money. Rate limits hit at the worst time.

**web-intel** runs Firecrawl on your own server — €5/month, unlimited scrapes, zero throttling. Wraps it in 5 clean functions and ships as both a Python library and an MCP server. Plug it into anything.

---

## What it does

```python
from web_intel import scrape, search, crawl, extract, extract_many

# Get clean markdown from any URL (JS-heavy sites included)
content = scrape("https://techcrunch.com/article")

# Search the web + get full page content
results = search("OpenAI funding round", limit=5, with_content=True)

# Crawl an entire site
pages = crawl("https://docs.example.com", max_pages=100)

# Pull exact structured data from any page
data = extract(
    url="https://company.com",
    schema={"company_name": str, "ceo": str, "revenue": str, "industry": str}
)
# → {"company_name": "Acme Corp", "ceo": "Jane Doe", "revenue": "$4.2B", ...}

# Batch extract from 100 URLs at once
leads = extract_many(urls=website_list, schema={"name": str, "email": str, "industry": str})
```

---

## The stack

```
Your code
    │
    ▼
web_intel (this library)
    │
    ├── Firecrawl  ──── self-hosted on your €5 VPS (no limits, no cost per call)
    │                   handles JS rendering, proxies, rate limits, retries
    │
    ├── SearXNG  ──── self-hosted search engine, routes through residential proxies
    │                 bypasses Google/Bing bot detection on datacenter IPs
    │
    └── LLM of your choice ──── OpenAI / NVIDIA NIM / Anthropic
                                 configured per-project via env vars
```

---

## Auto-saves everything

Every call automatically saves output to an `outputs/` folder — no extra code needed.

```
outputs/
├── 2026-05-10_06-32-11_techcrunch-com-article.md     # scrape
├── 2026-05-10_06-33-44_openai-funding-round.json      # search
├── 2026-05-10_06-35-02_docs-example-com.json          # crawl
└── 2026-05-10_06-36-19_company-com.json               # extract
```

Useful for debugging, piping into other tools, or just keeping a log of everything scraped.

---

## Auth-walled sites (LinkedIn etc.)

Add cookies to `cookies.json` at the root of the repo — they get auto-injected per domain:

```json
{
  "linkedin.com": "li_at=your_cookie_here"
}
```

No code changes. Any scrape of a matching domain gets the cookie header automatically.

To get your `li_at` cookie: Chrome → DevTools → Application → Cookies → `linkedin.com` → copy the `li_at` value.

---

## Live stats popup

Every `extract()` call fires a floating widget on your screen.

- Tokens used · Cost · URL scraped · Session total
- Draggable · Minimize to header · Error details on click
- Auto-spawns on first call, persists across runs

```bash
# Open manually anytime
python open_popup.py
# or
python -m web_intel.popup
```

---

## Setup

### 1. Self-host Firecrawl + SearXNG (one time, €5/month forever)

Spin up a VPS (Hetzner CX23 recommended — 4GB RAM, €5/month):

```bash
ssh root@your-server-ip
curl -fsSL https://get.docker.com | sh
git clone https://github.com/mendableai/firecrawl.git && cd firecrawl

cat > .env << 'EOF'
NUM_WORKERS_PER_QUEUE=8
PORT=3002
HOST=0.0.0.0
REDIS_URL=redis://redis:6379
REDIS_RATE_LIMIT_URL=redis://redis:6379
PLAYWRIGHT_MICROSERVICE_URL=http://playwright-service:3000/scrape
USE_DB_AUTHENTICATION=false
BULL_AUTH_KEY=your-secret-key
LOGGING_LEVEL=INFO
SEARXNG_ENDPOINT=http://searxng:8080
EOF

docker compose up -d
docker update --restart=always $(docker ps -q)
```

Firecrawl is now live at `http://your-server-ip:3002`. Unlimited. Forever.

**Fix SearXNG search on datacenter IPs (required):**

Datacenter IPs get blocked by Google/Bing. Route SearXNG through residential proxies:

1. Get free proxies from [webshare.io](https://webshare.io) (10 free, no credit card)
2. Go to Webshare → Free → Proxy Settings → IP Authorizations → add your server IP
3. Update SearXNG config inside the container:

```bash
docker exec firecrawl-searxng-1 python3 -c "
with open('/etc/searxng/settings.yml', 'r') as f:
    content = f.read()
# enable JSON format
content = content.replace('  formats:\n    - html\n', '  formats:\n    - html\n    - json\n', 1)
# add proxies (get IPs from Webshare Free → Proxy List)
content = content.replace('  #  proxies:', '  proxies:')
content = content.replace('  #    all://:', '    all://:')
content = content.replace('  #      - http://proxy1:8080', '      - http://PROXY_IP:PORT')
with open('/etc/searxng/settings.yml', 'w') as f:
    f.write(content)
"
docker restart firecrawl-searxng-1
```

### 2. Install web-intel

```bash
git clone https://github.com/yourusername/web-intel.git
cd web-intel
pip install -e .
```

### 3. Configure

```bash
cp .env.example .env
```

```env
# Point to your self-hosted instance
FIRECRAWL_API_KEY=your-secret-key
FIRECRAWL_URL=http://your-server-ip:3002

# Pick your LLM (only needed for extract)
WEB_INTEL_PROVIDER=openai         # openai | nvidia | anthropic
WEB_INTEL_API_KEY=sk-...
WEB_INTEL_MODEL=gpt-4o-mini
```

### 4. Verify

```bash
python tests/test_smoke.py
```

---

## Use as MCP server (for Claude / TRUMAN / any MCP host)

```python
# mcp_config.py
MCP_SERVERS = {
    "web_intel": {
        "command": "python",
        "args": ["-m", "web_intel.server"],
        "env": {
            "FIRECRAWL_API_KEY": "your-key",
            "FIRECRAWL_URL": "http://your-server-ip:3002",
            "WEB_INTEL_PROVIDER": "openai",
            "WEB_INTEL_API_KEY": "sk-...",
            "WEB_INTEL_MODEL": "gpt-4o-mini"
        }
    }
}
```

Instantly adds 5 tools: `web_intel__scrape` · `web_intel__search` · `web_intel__crawl` · `web_intel__extract` · `web_intel__extract_many`

---

## Provider routing

Same library, different brains per project:

```env
# Project A — OpenAI
WEB_INTEL_PROVIDER=openai
WEB_INTEL_API_KEY=sk-...
WEB_INTEL_MODEL=gpt-4o-mini

# Project B — NVIDIA NIM (free tier)
WEB_INTEL_PROVIDER=nvidia
WEB_INTEL_API_KEY=nvapi-...
WEB_INTEL_MODEL=meta/llama-3.3-70b-instruct
WEB_INTEL_BASE_URL=https://integrate.api.nvidia.com/v1
```

No code changes. Just swap env vars.

---

## Why self-host Firecrawl

| | Firecrawl Cloud | web-intel + self-hosted |
|---|---|---|
| Cost | Pay per scrape | €5/month flat |
| Rate limits | Yes | None |
| Data privacy | Their servers | Your server |
| Uptime control | Theirs | Yours |
| Scale | Expensive | Free |

---

## File structure

```
web_intel/
├── web_intel/
│   ├── __init__.py        # scrape, search, crawl, extract, extract_many
│   ├── config.py          # env var loading + provider routing
│   ├── server.py          # MCP server (5 tools)
│   ├── popup.py           # live stats widget controller
│   ├── _popup_window.py   # popup UI process
│   └── core/
│       ├── scrape.py      # single URL fetch + auto cookie inject
│       ├── crawl.py       # multi-page crawl
│       ├── search.py      # web search via SearXNG
│       ├── extract.py     # structured extraction
│       ├── output.py      # auto-save all results to outputs/
│       └── llm.py         # provider-agnostic LLM client
├── cookies.json           # domain → cookie string (auto-injected per domain)
├── outputs/               # auto-saved results (gitignored)
├── tests/test_smoke.py
├── open_popup.py          # double-click to open stats popup
├── setup.py
└── .env.example
```

---

## Built with

- [Firecrawl](https://github.com/mendableai/firecrawl) — web scraping engine
- [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai) — LLM extraction
- [MCP](https://modelcontextprotocol.io) — tool protocol

---

<p align="center">Built because paying per scrape is stupid.</p>
