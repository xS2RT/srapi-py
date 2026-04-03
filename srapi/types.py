from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional


@dataclass
class Link:
    relation: str
    uri: str

    @classmethod
    def from_dict(cls, d: dict) -> "Link":
        return cls(relation=d.get("rel", ""), uri=d.get("uri", ""))


@dataclass
class AssetLink:
    uri: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> Optional["AssetLink"]:
        if not d:
            return None
        return cls(uri=d.get("uri"), width=d.get("width"), height=d.get("height"))


class Duration:
    """A run time represented as floating-point seconds."""

    def __init__(self, seconds: float):
        self.seconds = seconds

    @classmethod
    def from_seconds(cls, s: Optional[float]) -> Optional["Duration"]:
        if s is None:
            return None
        return cls(s)

    def to_timedelta(self) -> timedelta:
        return timedelta(seconds=self.seconds)

    def __repr__(self) -> str:
        total = int(self.seconds)
        ms = round((self.seconds - total) * 1000)
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}.{ms:03d}"
        return f"{m}:{s:02d}.{ms:03d}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Duration):
            return self.seconds == other.seconds
        return NotImplemented

    def __lt__(self, other: "Duration") -> bool:
        if isinstance(other, Duration):
            return self.seconds < other.seconds
        return NotImplemented

    def __le__(self, other: "Duration") -> bool:
        if isinstance(other, Duration):
            return self.seconds <= other.seconds
        return NotImplemented


def parse_links(data: Optional[list]) -> List[Link]:
    if not data:
        return []
    return [Link.from_dict(l) for l in data]


def parse_assets(data: Optional[dict]) -> Dict[str, Optional[AssetLink]]:
    if not data:
        return {}
    return {k: AssetLink.from_dict(v) for k, v in data.items()}
