from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import AssetLink, Link, parse_assets, parse_links


@dataclass
class Series:
    id: str
    name_int: str
    abbreviation: str
    weblink: str
    moderators: Dict[str, str]  # {user_id: role}
    name_jap: Optional[str] = None
    created: Optional[str] = None
    assets: Dict[str, Optional[AssetLink]] = field(default_factory=dict)
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @property
    def name(self) -> str:
        return self.name_int

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Series":
        names = d.get("names", {})
        return cls(
            id=d["id"],
            name_int=names.get("international", ""),
            name_jap=names.get("japanese"),
            abbreviation=d.get("abbreviation", ""),
            weblink=d.get("weblink", ""),
            moderators=d.get("moderators") or {},
            created=d.get("created"),
            assets=parse_assets(d.get("assets")),
            links=parse_links(d.get("links")),
            _client=client,
        )

    def games(self, **kwargs):
        """Fetch games in this series."""
        return self._client.series_games(self.id, **kwargs)
