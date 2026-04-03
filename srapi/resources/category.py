from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..types import Link, parse_links


@dataclass
class PlayerRule:
    type: str   # 'exactly' or 'up-to'
    value: int


@dataclass
class Category:
    id: str
    name: str
    weblink: str
    type: str  # 'per-game' or 'per-level'
    players: PlayerRule
    miscellaneous: bool
    rules: Optional[str] = None
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Category":
        players_data = d.get("players", {})
        return cls(
            id=d["id"],
            name=d["name"],
            weblink=d.get("weblink", ""),
            type=d.get("type", "per-game"),
            players=PlayerRule(
                type=players_data.get("type", "exactly"),
                value=players_data.get("value", 1),
            ),
            miscellaneous=d.get("miscellaneous", False),
            rules=d.get("rules"),
            links=parse_links(d.get("links")),
            _client=client,
        )

    def variables(self, sort_by: Optional[str] = None, direction: Optional[str] = None):
        """Fetch variables defined for this category."""
        return self._client.category_variables(self.id, sort_by=sort_by, direction=direction)

    def records(self, top: int = 3, skip_empty: bool = False, embed=None):
        """Fetch top leaderboard entries for this category."""
        return self._client.category_records(self.id, top=top, skip_empty=skip_empty, embed=embed)
