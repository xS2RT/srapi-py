from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..types import Link, parse_links


@dataclass
class Level:
    id: str
    name: str
    weblink: str
    rules: Optional[str] = None
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Level":
        return cls(
            id=d["id"],
            name=d["name"],
            weblink=d.get("weblink", ""),
            rules=d.get("rules"),
            links=parse_links(d.get("links")),
            _client=client,
        )

    def categories(self, embed=None, sort_by: Optional[str] = None, direction: Optional[str] = None):
        """Fetch categories available for this level."""
        return self._client.level_categories(self.id, embed=embed, sort_by=sort_by, direction=direction)

    def variables(self, sort_by: Optional[str] = None, direction: Optional[str] = None):
        """Fetch variables scoped to this level."""
        return self._client.level_variables(self.id, sort_by=sort_by, direction=direction)

    def records(self, top: int = 3, skip_empty: bool = False, embed=None):
        """Fetch top leaderboard entries for this level."""
        return self._client.level_records(self.id, top=top, skip_empty=skip_empty, embed=embed)
