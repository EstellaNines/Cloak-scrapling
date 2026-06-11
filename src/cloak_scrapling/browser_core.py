from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


BrowserCoreProvider = Literal["env", "vendor", "cache", "download"]

PACKAGE_ROOT = Path(__file__).resolve().parent

PLATFORM_CHROMIUM_VERSIONS: dict[str, str] = {
    "linux-x64": "146.0.7680.177.5",
    "linux-arm64": "146.0.7680.177.3",
    "darwin-arm64": "145.0.7632.109.2",
    "darwin-x64": "145.0.7632.109.2",
    "windows-x64": "146.0.7680.177.5",
}

SUPPORTED_PLATFORMS: dict[tuple[str, str], str] = {
    ("Linux", "x86_64"): "linux-x64",
    ("Linux", "aarch64"): "linux-arm64",
    ("Darwin", "arm64"): "darwin-arm64",
    ("Darwin", "x86_64"): "darwin-x64",
    ("Windows", "AMD64"): "windows-x64",
    ("Windows", "x86_64"): "windows-x64",
}


@dataclass(frozen=True, slots=True)
class BrowserCoreInfo:
    platform: str
    version: str
    provider: BrowserCoreProvider
    binary_path: str
    installed: bool
    cache_dir: str
    vendor_dir: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "platform": self.platform,
            "version": self.version,
            "provider": self.provider,
            "binary_path": self.binary_path,
            "installed": self.installed,
            "cache_dir": self.cache_dir,
            "vendor_dir": self.vendor_dir,
        }


class BrowserCoreResolver:
    """Resolve the browser core path before CloakBrowser launches."""

    def __init__(
        self,
        *,
        platform_tag: str | None = None,
        chromium_version: str | None = None,
        vendor_root: Path | None = None,
        cache_root: Path | None = None,
    ) -> None:
        self.platform_tag = platform_tag or current_platform_tag()
        self.chromium_version = chromium_version or chromium_version_for_platform(
            self.platform_tag
        )
        self.vendor_root = vendor_root or default_vendor_root()
        self.cache_root = cache_root or default_cache_root()

    def resolve(self) -> BrowserCoreInfo:
        env_path = os.environ.get("CLOAKBROWSER_BINARY_PATH")
        vendor_dir = self.vendor_dir()
        cache_dir = self.cache_dir()

        if env_path:
            return BrowserCoreInfo(
                platform=self.platform_tag,
                version=self.chromium_version,
                provider="env",
                binary_path=env_path,
                installed=Path(env_path).exists(),
                cache_dir=str(cache_dir),
                vendor_dir=str(vendor_dir),
            )

        vendor_binary = self.vendor_binary_path()
        if is_usable_binary(vendor_binary):
            return BrowserCoreInfo(
                platform=self.platform_tag,
                version=self.chromium_version,
                provider="vendor",
                binary_path=str(vendor_binary),
                installed=True,
                cache_dir=str(cache_dir),
                vendor_dir=str(vendor_dir),
            )

        cache_binary = self.cache_binary_path()
        if is_usable_binary(cache_binary):
            return BrowserCoreInfo(
                platform=self.platform_tag,
                version=self.chromium_version,
                provider="cache",
                binary_path=str(cache_binary),
                installed=True,
                cache_dir=str(cache_dir),
                vendor_dir=str(vendor_dir),
            )

        return BrowserCoreInfo(
            platform=self.platform_tag,
            version=self.chromium_version,
            provider="download",
            binary_path=str(cache_binary),
            installed=False,
            cache_dir=str(cache_dir),
            vendor_dir=str(vendor_dir),
        )

    def apply_to_environment(self, info: BrowserCoreInfo) -> None:
        if info.provider == "vendor" and "CLOAKBROWSER_BINARY_PATH" not in os.environ:
            os.environ["CLOAKBROWSER_BINARY_PATH"] = info.binary_path

    def vendor_dir(self) -> Path:
        return self.vendor_root / self.platform_tag

    def cache_dir(self) -> Path:
        return self.cache_root / f"chromium-{self.chromium_version}"

    def vendor_binary_path(self) -> Path:
        return binary_path_for_platform(self.vendor_dir(), self.platform_tag)

    def cache_binary_path(self) -> Path:
        return binary_path_for_platform(self.cache_dir(), self.platform_tag)


def default_vendor_root() -> Path:
    override = os.environ.get("CLOAK_SCRAPLING_VENDOR_BROWSER_DIR")
    if override:
        return Path(override)
    site_root = PACKAGE_ROOT.parent
    candidates: list[Path] = []
    if (site_root.parent / "pyproject.toml").exists():
        candidates.append(site_root.parent / "vendor_browser")
    candidates.extend(
        [
            site_root / "vendor_browser",
            PACKAGE_ROOT / "vendor_browser",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def default_cache_root() -> Path:
    if os.environ.get("CLOAKBROWSER_CACHE_DIR"):
        return Path(os.environ["CLOAKBROWSER_CACHE_DIR"])
    if os.environ.get("CLOAK_SCRAPLING_CACHE_DIR"):
        return Path(os.environ["CLOAK_SCRAPLING_CACHE_DIR"])
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "CloakScrapling" / "cloakbrowser"
    return Path.home() / ".cache" / "cloak-scrapling" / "cloakbrowser"


def current_platform_tag() -> str:
    system = platform.system()
    machine = platform.machine()
    tag = SUPPORTED_PLATFORMS.get((system, machine))
    if tag is None:
        supported = ", ".join(f"{system}-{machine}" for system, machine in SUPPORTED_PLATFORMS)
        raise RuntimeError(f"Unsupported platform: {system} {machine}. Supported: {supported}")
    return tag


def chromium_version_for_platform(platform_tag: str) -> str:
    try:
        return PLATFORM_CHROMIUM_VERSIONS[platform_tag]
    except KeyError as exc:
        raise RuntimeError(f"Unsupported platform tag: {platform_tag}") from exc


def binary_path_for_platform(root: Path, platform_tag: str) -> Path:
    if platform_tag.startswith("darwin-"):
        return root / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
    if platform_tag.startswith("windows-"):
        return root / "chrome.exe"
    return root / "chrome"


def is_usable_binary(path: Path) -> bool:
    if not path.exists():
        return False
    if platform.system() == "Windows":
        return path.is_file()
    return path.is_file() and os.access(path, os.X_OK)


def resolve_browser_core_info() -> dict[str, str | bool]:
    return BrowserCoreResolver().resolve().to_dict()


def ensure_browser_core() -> str:
    os.environ.setdefault("CLOAKBROWSER_CACHE_DIR", str(default_cache_root()))

    from cloakbrowser.download import ensure_binary

    return ensure_binary()


def clear_browser_core_cache() -> None:
    os.environ.setdefault("CLOAKBROWSER_CACHE_DIR", str(default_cache_root()))

    from cloakbrowser.download import clear_cache

    clear_cache()
