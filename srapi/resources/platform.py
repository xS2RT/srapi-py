from dataclasses import dataclass, field
from typing import Any, List

from ..types import Link, parse_links


@dataclass
class Platform:
    id: str
    name: str
    released: int  # release year
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Platform":
        return cls(
            id=d["id"],
            name=d["name"],
            released=d.get("released", 0),
            links=parse_links(d.get("links")),
            _client=client,
        )

    def runs(self, **kwargs):
        """Fetch runs on this platform."""
        return self._client.runs(platform=self.id, **kwargs)
