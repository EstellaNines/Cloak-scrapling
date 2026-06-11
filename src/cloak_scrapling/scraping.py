from __future__ import annotations

from typing import Any

from .runtime import prepare_local_sources


async def fetch_page(
    cdp_url: str,
    url: str,
    *,
    console: Any | None = None,
    **kwargs: Any,
) -> Any:
    """Fetch a page through Scrapling's StealthyFetcher over an existing CDP URL."""
    prepare_local_sources()
    from scrapling.fetchers import StealthyFetcher

    kwargs.setdefault("google_search", False)
    _log(console, "input", "direct fetch requested", url=url, options=kwargs)
    try:
        page = await StealthyFetcher.async_fetch(url, cdp_url=cdp_url, **kwargs)
        _log(console, "output", "direct fetch completed", **summarize_page(page))
        return page
    except Exception as exc:
        _log(console, "error", "direct fetch failed", url=url, error=repr(exc))
        raise


async def mcp_stealthy_fetch(
    cdp_url: str,
    url: str,
    *,
    console: Any | None = None,
    **kwargs: Any,
) -> Any:
    """Fetch a page through ScraplingMCPServer over an existing CDP URL."""
    prepare_local_sources()
    from scrapling.core.ai import ScraplingMCPServer

    kwargs.setdefault("google_search", False)
    server = ScraplingMCPServer()
    _log(console, "input", "MCP stealthy_fetch requested", url=url, options=kwargs)
    try:
        result = await server.stealthy_fetch(url, cdp_url=cdp_url, **kwargs)
        _log(
            console,
            "mcp",
            "MCP stealthy_fetch completed",
            **summarize_mcp_result(result),
        )
        return result
    except Exception as exc:
        _log(console, "error", "MCP stealthy_fetch failed", url=url, error=repr(exc))
        raise


def summarize_page(page: Any) -> dict[str, Any]:
    title = None
    try:
        title = page.css("title::text").get()
    except Exception:
        title = None
    text = getattr(page, "text", "") or ""
    return {
        "status": getattr(page, "status", None),
        "url": getattr(page, "url", None),
        "title": title,
        "text_len": len(text),
        "preview": text[:160].replace("\n", " "),
    }


def summarize_mcp_result(result: Any) -> dict[str, Any]:
    content = getattr(result, "content", []) or []
    joined = " ".join(str(item).strip() for item in content if str(item).strip())
    return {
        "status": getattr(result, "status", None),
        "url": getattr(result, "url", None),
        "items": len(content),
        "preview": joined[:200].replace("\n", " "),
    }


def _log(console: Any | None, event: str, message: str, **fields: Any) -> None:
    if console is not None:
        console.log(event, message, **fields)
