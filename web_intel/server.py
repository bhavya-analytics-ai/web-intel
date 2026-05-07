"""
server.py — MCP server wrapper for web_intel.
Mount in TRUMAN, Claude Code, or any MCP-compatible system.

Run: python -m web_intel.server
"""
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .core.scrape import scrape
from .core.crawl import crawl
from .core.search import search
from .core.extract import extract, extract_many

app = Server("web_intel")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="web_intel__scrape",
            description="Fetch a URL and return clean markdown content. Handles JS-heavy sites.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to scrape"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="web_intel__search",
            description="Search the web and return results with optional full page content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Number of results", "default": 5},
                    "with_content": {"type": "boolean", "description": "Fetch full content", "default": False}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="web_intel__crawl",
            description="Crawl an entire website and return all pages as markdown.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Root URL to crawl"},
                    "max_pages": {"type": "integer", "description": "Max pages to crawl", "default": 50}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="web_intel__extract",
            description="Extract structured data from a URL using a schema.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to extract from"},
                    "schema": {"type": "object", "description": "Fields to extract e.g. {\"company_name\": \"str\"}"},
                    "prompt": {"type": "string", "description": "Optional extraction prompt"}
                },
                "required": ["url", "schema"]
            }
        ),
        Tool(
            name="web_intel__extract_many",
            description="Batch extract structured data from multiple URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {"type": "array", "items": {"type": "string"}, "description": "URLs to extract from"},
                    "schema": {"type": "object", "description": "Fields to extract"},
                    "prompt": {"type": "string", "description": "Optional extraction prompt"}
                },
                "required": ["urls", "schema"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "web_intel__scrape":
            result = scrape(arguments["url"])
        elif name == "web_intel__search":
            result = search(
                arguments["query"],
                limit=arguments.get("limit", 5),
                with_content=arguments.get("with_content", False)
            )
        elif name == "web_intel__crawl":
            result = crawl(arguments["url"], max_pages=arguments.get("max_pages", 50))
        elif name == "web_intel__extract":
            result = extract(
                arguments["url"],
                arguments["schema"],
                arguments.get("prompt")
            )
        elif name == "web_intel__extract_many":
            result = extract_many(
                arguments["urls"],
                arguments["schema"],
                arguments.get("prompt")
            )
        else:
            result = f"Unknown tool: {name}"

        output = result if isinstance(result, str) else json.dumps(result, indent=2)
        return [TextContent(type="text", text=output)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
