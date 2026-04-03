from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import Duration, Link, parse_links


@dataclass
class RunTimes:
    primary: Optional[Duration]
    realtime: Optional[Duration]
    realtime_noloads: Optional[Duration]
    ingame: Optional[Duration]

    @classmethod
    def from_dict(cls, d: dict) -> "RunTimes":
        return cls(
            primary=Duration.from_seconds(d.get("primary_t")),
            realtime=Duration.from_seconds(d.get("realtime_t")),
            realtime_noloads=Duration.from_seconds(d.get("realtime_noloads_t")),
            ingame=Duration.from_seconds(d.get("ingame_t")),
        )


@dataclass
class RunSystem:
    platform_id: Optional[str]
    emulated: bool
    region_id: Optional[str]


@dataclass
class RunStatus:
    status: str  # 'new', 'verified', 'rejected'
    examiner_id: Optional[str] = None
    verify_date: Optional[str] = None
    reason: Optional[str] = None  # rejection reason


@dataclass
class RunPlayer:
    type: str   # 'user' or 'guest'
    id: Optional[str] = None    # set for registered users
    name: Optional[str] = None  # set for guests (and optionally users)


@dataclass
class RunVideo:
    text: Optional[str]
    links: List[str]  # list of video URIs


def _get_id_or_embedded(val):
    """Return (id, embedded_dict) for a field that is either a plain ID string
    or an embedded object wrapped in {'data': {...}}."""
    if val is None:
        return None, None
    if isinstance(val, str):
        return val, None
    if isinstance(val, dict) and "data" in val:
        data = val["data"]
        return data.get("id"), data
    return None, None


@dataclass
class Run:
    id: str
    weblink: str
    game_id: str
    category_id: str
    times: RunTimes
    system: RunSystem
    status: RunStatus
    players: List[RunPlayer]
    values: Dict[str, str]
    level_id: Optional[str] = None
    date: Optional[str] = None
    submitted: Optional[str] = None
    videos: Optional[RunVideo] = None
    comment: Optional[str] = None
    splits: Optional[dict] = None
    links: List[Link] = field(default_factory=list)
    # Embedded data
    _game_data: Optional[dict] = field(default=None, repr=False)
    _level_data: Optional[dict] = field(default=None, repr=False)
    _category_data: Optional[dict] = field(default=None, repr=False)
    _platform_data: Optional[dict] = field(default=None, repr=False)
    _region_data: Optional[dict] = field(default=None, repr=False)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Run":
        game_id, game_data = _get_id_or_embedded(d.get("game"))
        level_id, level_data = _get_id_or_embedded(d.get("level"))
        category_id, category_data = _get_id_or_embedded(d.get("category"))

        sys_raw = d.get("system") or {}
        platform_val = sys_raw.get("platform")
        region_val = sys_raw.get("region")

        # platform/region inside system can also be embedded
        if isinstance(platform_val, dict) and "data" in platform_val:
            platform_id, platform_data = platform_val["data"].get("id"), platform_val["data"]
        else:
            platform_id, platform_data = platform_val, None

        if isinstance(region_val, dict) and "data" in region_val:
            region_id, region_data = region_val["data"].get("id"), region_val["data"]
        else:
            region_id, region_data = region_val, None

        system = RunSystem(
            platform_id=platform_id,
            emulated=sys_raw.get("emulated", False),
            region_id=region_id,
        )

        status_raw = d.get("status") or {}
        status = RunStatus(
            status=status_raw.get("status", "new"),
            examiner_id=status_raw.get("examiner"),
            verify_date=status_raw.get("verify-date"),
            reason=status_raw.get("reason"),
        )

        players_raw = d.get("players", [])
        players: List[RunPlayer] = []
        if isinstance(players_raw, dict) and "data" in players_raw:
            # embedded full user/guest objects
            for p in players_raw["data"]:
                if "id" in p:
                    players.append(RunPlayer(
                        type="user",
                        id=p["id"],
                        name=(p.get("names") or {}).get("international"),
                    ))
                else:
                    players.append(RunPlayer(type="guest", name=p.get("name")))
        else:
            for p in players_raw:
                if p.get("rel") == "user":
                    players.append(RunPlayer(type="user", id=p.get("id")))
                else:
                    players.append(RunPlayer(type="guest", name=p.get("name")))

        videos_raw = d.get("videos")
        videos = None
        if videos_raw:
            uris = [l.get("uri", "") for l in (videos_raw.get("links") or [])]
            videos = RunVideo(text=videos_raw.get("text"), links=uris)

        return cls(
            id=d["id"],
            weblink=d.get("weblink", ""),
            game_id=game_id or "",
            category_id=category_id or "",
            level_id=level_id,
            times=RunTimes.from_dict(d.get("times") or {}),
            system=system,
            status=status,
            players=players,
            values=d.get("values") or {},
            date=d.get("date"),
            submitted=d.get("submitted"),
            videos=videos,
            comment=d.get("comment"),
            splits=d.get("splits"),
            links=parse_links(d.get("links")),
            _game_data=game_data,
            _level_data=level_data,
            _category_data=category_data,
            _platform_data=platform_data,
            _region_data=region_data,
            _client=client,
        )

    def game(self):
        """Return the game (uses embedded data if available)."""
        if self._game_data:
            from .game import Game
            return Game.from_dict(self._game_data, self._client)
        return self._client.game(self.game_id)

    def category(self):
        """Return the category (uses embedded data if available)."""
        if self._category_data:
            from .category import Category
            return Category.from_dict(self._category_data, self._client)
        return self._client.category(self.category_id)

    def level(self):
        """Return the level for ILs, or None for full-game runs."""
        if self._level_data:
            from .level import Level
            return Level.from_dict(self._level_data, self._client)
        if self.level_id:
            return self._client.level(self.level_id)
        return None

    def platform(self):
        """Return the platform (uses embedded data if available)."""
        if self._platform_data:
            from .platform import Platform
            return Platform.from_dict(self._platform_data, self._client)
        if self.system.platform_id:
            return self._client.platform(self.system.platform_id)
        return None

    def region(self):
        """Return the region (uses embedded data if available)."""
        if self._region_data:
            from .region import Region
            return Region.from_dict(self._region_data, self._client)
        if self.system.region_id:
            return self._client.region(self.system.region_id)
        return None


@dataclass
class PersonalBest:
    place: int
    run: Run

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "PersonalBest":
        return cls(place=d["place"], run=Run.from_dict(d["run"], client))
