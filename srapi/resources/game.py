from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import AssetLink, Link, parse_assets, parse_links


@dataclass
class GameRuleset:
    show_milliseconds: bool = False
    require_verification: bool = True
    require_video: bool = False
    run_times: List[str] = field(default_factory=lambda: ["realtime"])
    default_time: str = "realtime"
    emulators_allowed: bool = True

    @classmethod
    def from_dict(cls, d: dict) -> "GameRuleset":
        return cls(
            show_milliseconds=d.get("show-milliseconds", False),
            require_verification=d.get("require-verification", True),
            require_video=d.get("require-video", False),
            run_times=d.get("run-times", ["realtime"]),
            default_time=d.get("default-time", "realtime"),
            emulators_allowed=d.get("emulators-allowed", True),
        )


def _extract_ids(val) -> List[str]:
    """Extract a list of IDs from either a plain list or an embedded {'data': [...]} object."""
    if not val:
        return []
    if isinstance(val, list):
        return [item["id"] if isinstance(item, dict) else item for item in val]
    if isinstance(val, dict):
        items = val.get("data", [])
        return [item["id"] if isinstance(item, dict) else item for item in items]
    return []


@dataclass
class Game:
    id: str
    name_int: str
    abbreviation: str
    weblink: str
    ruleset: GameRuleset
    name_jap: Optional[str] = None
    release_date: Optional[str] = None
    created: Optional[str] = None
    platform_ids: List[str] = field(default_factory=list)
    region_ids: List[str] = field(default_factory=list)
    genre_ids: List[str] = field(default_factory=list)
    developer_ids: List[str] = field(default_factory=list)
    publisher_ids: List[str] = field(default_factory=list)
    gametype_ids: List[str] = field(default_factory=list)
    moderators: Dict[str, str] = field(default_factory=dict)  # {user_id: role}
    assets: Dict[str, Optional[AssetLink]] = field(default_factory=dict)
    links: List[Link] = field(default_factory=list)
    # Embedded data (populated when embed= was used)
    _categories_data: Optional[List[dict]] = field(default=None, repr=False)
    _levels_data: Optional[List[dict]] = field(default=None, repr=False)
    _client: Any = field(default=None, repr=False, compare=False)

    @property
    def name(self) -> str:
        return self.name_int

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Game":
        names = d.get("names", {})

        cats_raw = d.get("categories")
        levels_raw = d.get("levels")
        cats_data = cats_raw.get("data") if isinstance(cats_raw, dict) else None
        levels_data = levels_raw.get("data") if isinstance(levels_raw, dict) else None

        return cls(
            id=d["id"],
            name_int=names.get("international", ""),
            name_jap=names.get("japanese"),
            abbreviation=d.get("abbreviation", ""),
            weblink=d.get("weblink", ""),
            ruleset=GameRuleset.from_dict(d.get("ruleset") or {}),
            release_date=d.get("release-date"),
            created=d.get("created"),
            platform_ids=_extract_ids(d.get("platforms")),
            region_ids=_extract_ids(d.get("regions")),
            genre_ids=_extract_ids(d.get("genres")),
            developer_ids=_extract_ids(d.get("developers")),
            publisher_ids=_extract_ids(d.get("publishers")),
            gametype_ids=_extract_ids(d.get("gametypes")),
            moderators=d.get("moderators") or {},
            assets=parse_assets(d.get("assets")),
            links=parse_links(d.get("links")),
            _categories_data=cats_data,
            _levels_data=levels_data,
            _client=client,
        )

    def categories(self, miscellaneous: Optional[bool] = None, sort_by=None, direction=None):
        """Fetch categories for this game (uses embedded data if available)."""
        if self._categories_data is not None:
            from .category import Category
            return [Category.from_dict(c, self._client) for c in self._categories_data]
        return self._client.game_categories(
            self.id, miscellaneous=miscellaneous, sort_by=sort_by, direction=direction
        )

    def levels(self, sort_by=None, direction=None):
        """Fetch levels for this game (uses embedded data if available)."""
        if self._levels_data is not None:
            from .level import Level
            return [Level.from_dict(l, self._client) for l in self._levels_data]
        return self._client.game_levels(self.id, sort_by=sort_by, direction=direction)

    def variables(self, sort_by=None, direction=None):
        """Fetch variables defined for this game."""
        return self._client.game_variables(self.id, sort_by=sort_by, direction=direction)

    def derived_games(self, **kwargs):
        """Fetch games derived from this game (ROM hacks, fan games, etc.)."""
        return self._client.game_derived_games(self.id, **kwargs)

    def records(
        self,
        top: int = 3,
        scope: Optional[str] = None,
        miscellaneous: Optional[bool] = None,
        skip_empty: bool = False,
        embed=None,
    ):
        """Fetch leaderboard records for this game."""
        return self._client.game_records(
            self.id,
            top=top,
            scope=scope,
            miscellaneous=miscellaneous,
            skip_empty=skip_empty,
            embed=embed,
        )

    def leaderboard(self, category: str, **kwargs):
        """Fetch the full-game leaderboard for a category."""
        return self._client.leaderboard(self.id, category, **kwargs)
