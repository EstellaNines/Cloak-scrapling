"""CloakBrowser + Scrapling integration helpers."""

from .browser_models import (
    BrowserActionResult,
    BrowserElement,
    BrowserOpenResult,
    BrowserState,
)
from .browser_core import BrowserCoreInfo, BrowserCoreResolver
from .bridge import CloakScraplingBridge, CloakScraplingConfig
from .session import CloakScraplingSession

__all__ = [
    "BrowserActionResult",
    "BrowserCoreInfo",
    "BrowserCoreResolver",
    "BrowserElement",
    "BrowserOpenResult",
    "BrowserState",
    "CloakScraplingBridge",
    "CloakScraplingConfig",
    "CloakScraplingSession",
]
