from dataclasses import dataclass, field
from typing import Any, List

from ..types import Link, parse_links


@dataclass
class Guest:
    name: str
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Guest":
        return cls(
            name=d["name"],
            links=parse_links(d.get("links")),
            _client=client,
        )

    def runs(self, **kwargs):
        """Fetch runs submitted by this guest."""
        return self._client.runs(guest=self.name, **kwargs)
