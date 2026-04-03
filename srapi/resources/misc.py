"""Simple single-field resources: Engine, Developer, Publisher, GameType, Genre."""

from dataclasses import dataclass, field
from typing import Any, List

from ..types import Link, parse_links


@dataclass
class Engine:
    id: str
    name: str
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Engine":
        return cls(id=d["id"], name=d["name"], links=parse_links(d.get("links")), _client=client)


@dataclass
class Developer:
    id: str
    name: str
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Developer":
        return cls(id=d["id"], name=d["name"], links=parse_links(d.get("links")), _client=client)


@dataclass
class Publisher:
    id: str
    name: str
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Publisher":
        return cls(id=d["id"], name=d["name"], links=parse_links(d.get("links")), _client=client)


@dataclass
class GameType:
    id: str
    name: str
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "GameType":
        return cls(id=d["id"], name=d["name"], links=parse_links(d.get("links")), _client=client)


@dataclass
class Genre:
    id: str
    name: str
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Genre":
        return cls(id=d["id"], name=d["name"], links=parse_links(d.get("links")), _client=client)
