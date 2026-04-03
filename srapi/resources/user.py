from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..types import Link, parse_links


@dataclass
class UserLocation:
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None


@dataclass
class UserNameStyle:
    style: str = "solid"  # 'solid' or 'gradient'
    color_from_light: Optional[str] = None
    color_from_dark: Optional[str] = None
    color_to_light: Optional[str] = None
    color_to_dark: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "UserNameStyle":
        style = d.get("style", "solid")
        if style == "solid":
            color = d.get("color") or {}
            return cls(
                style=style,
                color_from_light=color.get("light"),
                color_from_dark=color.get("dark"),
            )
        # gradient
        cf = d.get("color-from") or {}
        ct = d.get("color-to") or {}
        return cls(
            style=style,
            color_from_light=cf.get("light"),
            color_from_dark=cf.get("dark"),
            color_to_light=ct.get("light"),
            color_to_dark=ct.get("dark"),
        )


@dataclass
class User:
    id: str
    weblink: str
    name_int: str
    role: str
    name_jap: Optional[str] = None
    pronouns: Optional[str] = None
    signup: Optional[str] = None
    location: Optional[UserLocation] = None
    name_style: Optional[UserNameStyle] = None
    twitch: Optional[str] = None
    hitbox: Optional[str] = None
    youtube: Optional[str] = None
    twitter: Optional[str] = None
    speedrunslive: Optional[str] = None
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @property
    def name(self) -> str:
        return self.name_int

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "User":
        names = d.get("names", {})

        location_data = d.get("location")
        location = None
        if location_data:
            country = location_data.get("country") or {}
            reg = location_data.get("region") or {}
            location = UserLocation(
                country_code=country.get("code"),
                country_name=(country.get("names") or {}).get("international"),
                region_code=reg.get("code"),
                region_name=(reg.get("names") or {}).get("international"),
            )

        style_data = d.get("name-style") or {}
        name_style = UserNameStyle.from_dict(style_data) if style_data else None

        def social_uri(key: str) -> Optional[str]:
            val = d.get(key)
            if isinstance(val, dict):
                return val.get("uri")
            return None

        return cls(
            id=d["id"],
            weblink=d.get("weblink", ""),
            name_int=names.get("international", ""),
            name_jap=names.get("japanese"),
            pronouns=d.get("pronouns"),
            signup=d.get("signup"),
            role=d.get("role", "user"),
            location=location,
            name_style=name_style,
            twitch=social_uri("twitch"),
            hitbox=social_uri("hitbox"),
            youtube=social_uri("youtube"),
            twitter=social_uri("twitter"),
            speedrunslive=social_uri("speedrunslive"),
            links=parse_links(d.get("links")),
            _client=client,
        )

    def personal_bests(
        self,
        top: Optional[int] = None,
        series: Optional[str] = None,
        game: Optional[str] = None,
        embed=None,
    ):
        """Fetch this user's personal bests."""
        return self._client.user_personal_bests(
            self.id, top=top, series=series, game=game, embed=embed
        )

    def runs(self, **kwargs):
        """Fetch runs submitted by this user."""
        return self._client.runs(user=self.id, **kwargs)
