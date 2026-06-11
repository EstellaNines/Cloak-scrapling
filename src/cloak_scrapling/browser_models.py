from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BrowserElement:
    index: int
    tag: str
    text: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "tag": self.tag,
            "text": self.text,
            "attributes": dict(self.attributes),
        }

    def to_text(self) -> str:
        attrs = " ".join(
            f'{name}="{_quote(value)}"'
            for name, value in self.attributes.items()
            if value
        )
        open_tag = f"[{self.index}]<{self.tag}"
        if attrs:
            open_tag = f"{open_tag} {attrs}"
        if self.text:
            return f"{open_tag}>{_quote(self.text)}</{self.tag}>"
        return f"{open_tag} />"


@dataclass(slots=True)
class BrowserState:
    url: str
    title: str
    elements: list[BrowserElement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "elements": [element.to_dict() for element in self.elements],
            "text": self.to_text(),
        }

    def to_text(self) -> str:
        lines = [f"url={self.url}", f"title={self.title}"]
        if self.elements:
            lines.append("")
            lines.extend(element.to_text() for element in self.elements)
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class BrowserOpenResult:
    status: int | None
    url: str
    title: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "url": self.url,
            "title": self.title,
        }


@dataclass(frozen=True, slots=True)
class BrowserActionResult:
    action: str
    url: str | None = None
    index: int | None = None
    value: str | int | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"action": self.action}
        if self.url is not None:
            result["url"] = self.url
        if self.index is not None:
            result["index"] = self.index
        if self.value is not None:
            result["value"] = self.value
        return result


def _quote(value: str) -> str:
    return value.replace("\n", " ").replace('"', "&quot;").strip()
