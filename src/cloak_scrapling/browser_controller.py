from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .browser_models import BrowserElement, BrowserState


INTERACTIVE_SELECTOR = ", ".join(
    [
        "a[href]",
        "button",
        "input",
        "textarea",
        "select",
        "[role=button]",
        "[contenteditable]",
    ]
)


ELEMENT_INFO_SCRIPT = """
element => {
  const rect = element.getBoundingClientRect();
  const visible = !!(
    rect.width &&
    rect.height &&
    window.getComputedStyle(element).visibility !== "hidden" &&
    window.getComputedStyle(element).display !== "none"
  );
  const clean = value => (value || "").toString().replace(/\\s+/g, " ").trim();
  const tag = element.tagName.toLowerCase();
  const text = clean(
    element.innerText ||
    element.value ||
    element.getAttribute("aria-label") ||
    element.getAttribute("placeholder") ||
    element.textContent
  ).slice(0, 120);
  const attrs = {};
  for (const name of ["type", "role", "name", "placeholder", "aria-label", "href"]) {
    const value = name === "href" && element.href ? element.href : element.getAttribute(name);
    if (value) {
      attrs[name] = clean(value).slice(0, 160);
    }
  }
  return { tag, text, attrs, visible };
}
"""


class BrowserController:
    """Control a CloakBrowser page through the browser CDP WebSocket."""

    def __init__(
        self,
        cdp_url: str,
        *,
        default_screenshot_dir: Path | None = None,
    ) -> None:
        self.cdp_url = cdp_url
        self.default_screenshot_dir = default_screenshot_dir or Path(".logs")
        self._playwright: Any | None = None
        self._browser: Any | None = None
        self._context: Any | None = None
        self._page: Any | None = None
        self._elements: dict[int, Any] = {}

    async def connect(self) -> None:
        if self._browser is not None:
            return
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is required for interactive browser commands. "
                "Install cloak-scrapling with its declared dependencies."
            ) from exc

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(
                self.cdp_url
            )
        except Exception as exc:
            await self.close()
            raise RuntimeError(
                "Could not connect to CloakBrowser over CDP. "
                f"CDP URL was {self.cdp_url!r}; ensure the browser is running and CDP is ready."
            ) from exc

    async def ensure_page(self) -> Any:
        await self.connect()
        if self._page is not None and not self._page.is_closed():
            return self._page

        contexts = list(self._browser.contexts)
        self._context = contexts[0] if contexts else await self._browser.new_context()
        pages = list(self._context.pages)
        self._page = pages[0] if pages else await self._context.new_page()
        return self._page

    async def open_url(
        self,
        url: str,
        *,
        wait_until: str = "domcontentloaded",
        timeout: int | float = 30000,
    ) -> dict[str, Any]:
        page = await self.ensure_page()
        response = await page.goto(url, wait_until=wait_until, timeout=timeout)
        return {
            "status": response.status if response is not None else None,
            "url": page.url,
            "title": await page.title(),
        }

    async def state(self) -> BrowserState:
        page = await self.ensure_page()
        await self._clear_elements()
        handles = await page.query_selector_all(INTERACTIVE_SELECTOR)
        elements: list[BrowserElement] = []
        next_index = 1
        for handle in handles:
            info = await handle.evaluate(ELEMENT_INFO_SCRIPT)
            if not info.get("visible"):
                await _dispose(handle)
                continue
            element = BrowserElement(
                index=next_index,
                tag=str(info.get("tag") or "element"),
                text=str(info.get("text") or ""),
                attributes={
                    str(k): str(v)
                    for k, v in dict(info.get("attrs") or {}).items()
                },
            )
            self._elements[next_index] = handle
            elements.append(element)
            next_index += 1

        return BrowserState(
            url=page.url,
            title=await page.title(),
            elements=elements,
        )

    async def click(self, index: int) -> dict[str, Any]:
        handle = self._get_element(index)
        await handle.click()
        page = await self.ensure_page()
        return {"clicked": index, "url": page.url}

    async def input_text(self, index: int, text: str) -> dict[str, Any]:
        handle = self._get_element(index)
        await handle.fill(text)
        return {"input": index, "text_length": len(text)}

    async def press(self, key: str) -> dict[str, Any]:
        page = await self.ensure_page()
        await page.keyboard.press(key)
        return {"pressed": key, "url": page.url}

    async def scroll(self, direction: str, amount: int = 800) -> dict[str, Any]:
        page = await self.ensure_page()
        delta = self.scroll_delta(direction, amount)
        await page.mouse.wheel(0, delta)
        return {"direction": direction, "delta_y": delta, "url": page.url}

    async def screenshot(self, path: str | Path | None = None) -> dict[str, Any]:
        page = await self.ensure_page()
        screenshot_path = Path(path) if path else self.default_screenshot_path()
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot_path), full_page=True)
        return {"path": str(screenshot_path)}

    async def get_text(self, selector: str | None = None) -> str:
        page = await self.ensure_page()
        target = page.locator(selector or "body").first
        return await target.inner_text()

    async def get_html(self, selector: str | None = None) -> str:
        page = await self.ensure_page()
        if selector:
            return await page.locator(selector).first.evaluate(
                "element => element.outerHTML"
            )
        return await page.content()

    async def close(self) -> None:
        await self._clear_elements()
        try:
            if self._browser is not None:
                await self._browser.close()
        finally:
            self._browser = None
            self._context = None
            self._page = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None

    def default_screenshot_path(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return self.default_screenshot_dir / f"screenshot-{timestamp}.png"

    @staticmethod
    def scroll_delta(direction: str, amount: int = 800) -> int:
        normalized = direction.lower()
        if normalized == "down":
            return amount
        if normalized == "up":
            return -amount
        raise ValueError("direction must be 'up' or 'down'")

    def _get_element(self, index: int) -> Any:
        try:
            return self._elements[index]
        except KeyError as exc:
            raise ValueError(
                "element index is not available; run state before interacting"
            ) from exc

    async def _clear_elements(self) -> None:
        handles = list(self._elements.values())
        self._elements.clear()
        for handle in handles:
            await _dispose(handle)


async def _dispose(handle: Any) -> None:
    try:
        await handle.dispose()
    except Exception:
        pass
