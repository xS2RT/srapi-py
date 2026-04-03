from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..types import Link, parse_links
from .run import Run


def _extract_id(val) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        data = val.get("data", val)
        if isinstance(data, dict):
            return data.get("id")
    return None


@dataclass
class LeaderboardEntry:
    place: int
    run: Run


@dataclass
class Leaderboard:
    weblink: str
    game_id: str
    category_id: str
    runs: List[LeaderboardEntry]
    level_id: Optional[str] = None
    platform_id: Optional[str] = None
    region_id: Optional[str] = None
    emulators_only: bool = False
    video_only: bool = False
    timing: str = "realtime"
    date: Optional[str] = None
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Leaderboard":
        entries = [
            LeaderboardEntry(place=e["place"], run=Run.from_dict(e["run"], client))
            for e in d.get("runs", [])
        ]
        return cls(
            weblink=d.get("weblink", ""),
            game_id=_extract_id(d.get("game")) or "",
            category_id=_extract_id(d.get("category")) or "",
            level_id=_extract_id(d.get("level")),
            platform_id=_extract_id(d.get("platform")),
            region_id=_extract_id(d.get("region")),
            emulators_only=d.get("emulators-only", False),
            video_only=d.get("video-only", False),
            timing=d.get("timing", "realtime"),
            date=d.get("date"),
            runs=entries,
            links=parse_links(d.get("links")),
            _client=client,
        )

    def game(self):
        return self._client.game(self.game_id)

    def category(self):
        return self._client.category(self.category_id)

    def level(self):
        if self.level_id:
            return self._client.level(self.level_id)
        return None
