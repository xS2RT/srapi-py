from typing import Any, Dict, List, Optional

import requests

from .collection import Collection
from .errors import SrapiError
from .resources.category import Category
from .resources.game import Game
from .resources.guest import Guest
from .resources.leaderboard import Leaderboard
from .resources.level import Level
from .resources.misc import Developer, Engine, GameType, Genre, Publisher
from .resources.notification import Notification
from .resources.platform import Platform
from .resources.region import Region
from .resources.run import PersonalBest, Run
from .resources.series import Series
from .resources.user import User
from .resources.variable import Variable

BASE_URL = "https://www.speedrun.com/api/v1"


class Client:
    """Client for the speedrun.com REST API v1.

    Args:
        api_key: Your speedrun.com API key. Required for authenticated
            endpoints (profile, notifications, run submission).
        user_agent: Custom User-Agent header value.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_agent: str = "srapi-py/1.0",
    ):
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        path: str,
        params: Optional[dict] = None,
        method: str = "GET",
        json: Optional[dict] = None,
    ) -> dict:
        url = f"{BASE_URL}{path}"
        headers: dict = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        try:
            resp = self._session.request(
                method,
                url,
                params=clean_params,
                json=json,
                headers=headers,
                timeout=30,
            )
        except requests.Timeout:
            raise SrapiError("Request timed out", url=url)
        except requests.ConnectionError as exc:
            raise SrapiError(f"Connection error: {exc}", url=url)

        if resp.status_code == 420:
            raise SrapiError("Rate limit exceeded", status_code=420, url=url)
        if not resp.ok:
            try:
                msg = resp.json().get("message", resp.text)
            except Exception:
                msg = resp.text
            raise SrapiError(msg, status_code=resp.status_code, url=url)

        return resp.json()

    def _collection(
        self,
        path: str,
        parse_fn: Any,
        params: Optional[dict] = None,
        max_per_page: int = 200,
    ) -> Collection:
        return Collection(self, path, params or {}, parse_fn, max_per_page)

    @staticmethod
    def _embed(embed: Optional[List[str]]) -> Optional[str]:
        return ",".join(embed) if embed else None

    def _require_auth(self) -> None:
        if not self.api_key:
            raise SrapiError("An API key is required for this endpoint")

    # ------------------------------------------------------------------
    # Games
    # ------------------------------------------------------------------

    def game(self, id_or_abbr: str, embed: Optional[List[str]] = None) -> Game:
        """Fetch a single game by ID or abbreviation."""
        data = self._request(f"/games/{id_or_abbr}", {"embed": self._embed(embed)})
        return Game.from_dict(data["data"], self)

    def games(
        self,
        name: Optional[str] = None,
        platform: Optional[str] = None,
        region: Optional[str] = None,
        genre: Optional[str] = None,
        developer: Optional[str] = None,
        publisher: Optional[str] = None,
        released: Optional[int] = None,
        gametype: Optional[str] = None,
        moderator: Optional[str] = None,
        bulk: bool = False,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List games with optional filters.

        Set ``bulk=True`` to request up to 1000 games per page (only id,
        names, abbreviation, and weblink are returned in bulk mode).
        """
        params: dict = {
            "name": name,
            "platform": platform,
            "region": region,
            "genre": genre,
            "developer": developer,
            "publisher": publisher,
            "released": released,
            "gametype": gametype,
            "moderator": moderator,
            "embed": self._embed(embed),
            "orderby": sort_by,
            "direction": direction,
        }
        if bulk:
            params["_bulk"] = "yes"
        max_pp = 1000 if bulk else 200
        return self._collection("/games", lambda d, c: Game.from_dict(d, c), params, max_pp)

    def game_categories(
        self,
        game_id: str,
        miscellaneous: Optional[bool] = None,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List categories for a game."""
        params: dict = {
            "embed": self._embed(embed),
            "orderby": sort_by,
            "direction": direction,
        }
        if miscellaneous is not None:
            params["miscellaneous"] = "yes" if miscellaneous else "no"
        return self._collection(
            f"/games/{game_id}/categories", lambda d, c: Category.from_dict(d, c), params
        )

    def game_levels(
        self,
        game_id: str,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List levels for a game."""
        params = {"embed": self._embed(embed), "orderby": sort_by, "direction": direction}
        return self._collection(
            f"/games/{game_id}/levels", lambda d, c: Level.from_dict(d, c), params
        )

    def game_variables(
        self,
        game_id: str,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List variables defined for a game."""
        params = {"orderby": sort_by, "direction": direction}
        return self._collection(
            f"/games/{game_id}/variables", lambda d, c: Variable.from_dict(d, c), params
        )

    def game_derived_games(
        self,
        game_id: str,
        name: Optional[str] = None,
        platform: Optional[str] = None,
        region: Optional[str] = None,
        genre: Optional[str] = None,
        developer: Optional[str] = None,
        publisher: Optional[str] = None,
        released: Optional[int] = None,
        gametype: Optional[str] = None,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List games derived from this game (ROM hacks, translations, etc.)."""
        params = {
            "name": name, "platform": platform, "region": region,
            "genre": genre, "developer": developer, "publisher": publisher,
            "released": released, "gametype": gametype,
            "embed": self._embed(embed),
            "orderby": sort_by, "direction": direction,
        }
        return self._collection(
            f"/games/{game_id}/derived-games", lambda d, c: Game.from_dict(d, c), params
        )

    def game_records(
        self,
        game_id: str,
        top: int = 3,
        scope: Optional[str] = None,
        miscellaneous: Optional[bool] = None,
        skip_empty: bool = False,
        embed: Optional[List[str]] = None,
    ) -> Collection:
        """List leaderboard records for every category in a game."""
        params: dict = {
            "top": top,
            "scope": scope,
            "embed": self._embed(embed),
        }
        if miscellaneous is not None:
            params["miscellaneous"] = "yes" if miscellaneous else "no"
        if skip_empty:
            params["skip-empty"] = "yes"
        return self._collection(
            f"/games/{game_id}/records", lambda d, c: Leaderboard.from_dict(d, c), params
        )

    # ------------------------------------------------------------------
    # Runs
    # ------------------------------------------------------------------

    def run(self, run_id: str, embed: Optional[List[str]] = None) -> Run:
        """Fetch a single run by ID."""
        data = self._request(f"/runs/{run_id}", {"embed": self._embed(embed)})
        return Run.from_dict(data["data"], self)

    def runs(
        self,
        user: Optional[str] = None,
        guest: Optional[str] = None,
        examiner: Optional[str] = None,
        game: Optional[str] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        region: Optional[str] = None,
        emulated: Optional[bool] = None,
        status: Optional[str] = None,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List runs with optional filters.

        ``status`` can be ``'new'``, ``'verified'``, or ``'rejected'``.
        ``sort_by`` can be ``'game'``, ``'category'``, ``'level'``, ``'platform'``,
        ``'region'``, ``'emulated'``, ``'date'``, ``'submitted'``, ``'status'``,
        or ``'verify-date'``.
        """
        params: dict = {
            "user": user, "guest": guest, "examiner": examiner,
            "game": game, "level": level, "category": category,
            "platform": platform, "region": region,
            "status": status,
            "embed": self._embed(embed),
            "orderby": sort_by,
            "direction": direction,
        }
        if emulated is True:
            params["emulated"] = "yes"
        return self._collection("/runs", lambda d, c: Run.from_dict(d, c), params)

    def submit_run(
        self,
        category: str,
        times: dict,
        level: Optional[str] = None,
        date: Optional[str] = None,
        region: Optional[str] = None,
        platform: Optional[str] = None,
        verified: Optional[bool] = None,
        video: Optional[str] = None,
        comment: Optional[str] = None,
        splitsio: Optional[str] = None,
        players: Optional[List[dict]] = None,
        emulated: bool = False,
        variables: Optional[dict] = None,
    ) -> Run:
        """Submit a new run. Requires authentication.

        ``times`` should be a dict with at least one of: ``realtime``,
        ``realtime_noloads``, ``ingame`` (ISO 8601 duration strings, e.g.
        ``"PT1H23M45S"``).
        ``players`` is a list of ``{"rel": "user", "id": "..."}`` or
        ``{"rel": "guest", "name": "..."}`` dicts.
        ``variables`` is a dict mapping variable ID → value ID.
        """
        self._require_auth()
        body: dict = {
            "category": category,
            "times": times,
            "emulated": emulated,
        }
        for key, val in [
            ("level", level), ("date", date), ("region", region),
            ("platform", platform), ("verified", verified),
            ("comment", comment), ("splitsio", splitsio),
        ]:
            if val is not None:
                body[key] = val
        if video:
            body["videos"] = {"links": [{"uri": video}]}
        if players:
            body["players"] = players
        if variables:
            body["variables"] = {vid: {"type": "pre-defined", "value": val} for vid, val in variables.items()}

        data = self._request("/runs", method="POST", json=body)
        return Run.from_dict(data["data"], self)

    def update_run_status(
        self,
        run_id: str,
        status: str,
        reason: Optional[str] = None,
    ) -> None:
        """Update verification status of a run. Requires moderator privileges."""
        self._require_auth()
        payload: dict = {"status": status}
        if reason and status == "rejected":
            payload["reason"] = reason
        self._request(f"/runs/{run_id}/status", method="PUT", json={"status": payload})

    def update_run_players(self, run_id: str, players: List[dict]) -> None:
        """Replace the player list of a run. Requires moderator privileges."""
        self._require_auth()
        self._request(f"/runs/{run_id}/players", method="PUT", json={"players": players})

    def delete_run(self, run_id: str) -> None:
        """Delete a run. Requires authentication."""
        self._require_auth()
        self._request(f"/runs/{run_id}", method="DELETE")

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def user(self, id_or_name: str) -> User:
        """Fetch a single user by ID or username."""
        data = self._request(f"/users/{id_or_name}")
        return User.from_dict(data["data"], self)

    def users(
        self,
        name: Optional[str] = None,
        lookup: Optional[str] = None,
        twitch: Optional[str] = None,
        hitbox: Optional[str] = None,
        youtube: Optional[str] = None,
        twitter: Optional[str] = None,
        speedrunslive: Optional[str] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """Search users. At least one filter must be provided."""
        params = {
            "name": name, "lookup": lookup, "twitch": twitch,
            "hitbox": hitbox, "youtube": youtube, "twitter": twitter,
            "speedrunslive": speedrunslive,
            "orderby": sort_by, "direction": direction,
        }
        return self._collection("/users", lambda d, c: User.from_dict(d, c), params)

    def user_personal_bests(
        self,
        user_id: str,
        top: Optional[int] = None,
        series: Optional[str] = None,
        game: Optional[str] = None,
        embed: Optional[List[str]] = None,
    ) -> List[PersonalBest]:
        """Fetch a user's personal best runs."""
        params = {"top": top, "series": series, "game": game, "embed": self._embed(embed)}
        data = self._request(f"/users/{user_id}/personal-bests", params)
        return [PersonalBest.from_dict(e, self) for e in data.get("data", [])]

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def category(self, category_id: str, embed: Optional[List[str]] = None) -> Category:
        """Fetch a single category by ID."""
        data = self._request(f"/categories/{category_id}", {"embed": self._embed(embed)})
        return Category.from_dict(data["data"], self)

    def category_variables(
        self,
        category_id: str,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List variables for a category."""
        params = {"orderby": sort_by, "direction": direction}
        return self._collection(
            f"/categories/{category_id}/variables",
            lambda d, c: Variable.from_dict(d, c),
            params,
        )

    def category_records(
        self,
        category_id: str,
        top: int = 3,
        skip_empty: bool = False,
        embed: Optional[List[str]] = None,
    ) -> Collection:
        """List top leaderboard entries for a category."""
        params: dict = {"top": top, "embed": self._embed(embed)}
        if skip_empty:
            params["skip-empty"] = "yes"
        return self._collection(
            f"/categories/{category_id}/records",
            lambda d, c: Leaderboard.from_dict(d, c),
            params,
        )

    # ------------------------------------------------------------------
    # Levels
    # ------------------------------------------------------------------

    def level(self, level_id: str, embed: Optional[List[str]] = None) -> Level:
        """Fetch a single level by ID."""
        data = self._request(f"/levels/{level_id}", {"embed": self._embed(embed)})
        return Level.from_dict(data["data"], self)

    def level_categories(
        self,
        level_id: str,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List categories for a level."""
        params = {"embed": self._embed(embed), "orderby": sort_by, "direction": direction}
        return self._collection(
            f"/levels/{level_id}/categories", lambda d, c: Category.from_dict(d, c), params
        )

    def level_variables(
        self,
        level_id: str,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List variables scoped to a level."""
        params = {"orderby": sort_by, "direction": direction}
        return self._collection(
            f"/levels/{level_id}/variables", lambda d, c: Variable.from_dict(d, c), params
        )

    def level_records(
        self,
        level_id: str,
        top: int = 3,
        skip_empty: bool = False,
        embed: Optional[List[str]] = None,
    ) -> Collection:
        """List top leaderboard entries for a level."""
        params: dict = {"top": top, "embed": self._embed(embed)}
        if skip_empty:
            params["skip-empty"] = "yes"
        return self._collection(
            f"/levels/{level_id}/records", lambda d, c: Leaderboard.from_dict(d, c), params
        )

    # ------------------------------------------------------------------
    # Leaderboards
    # ------------------------------------------------------------------

    def leaderboard(
        self,
        game: str,
        category: str,
        top: Optional[int] = None,
        platform: Optional[str] = None,
        region: Optional[str] = None,
        video_only: bool = False,
        timing: Optional[str] = None,
        date: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        embed: Optional[List[str]] = None,
    ) -> Leaderboard:
        """Fetch a full-game leaderboard.

        ``variables`` filters by variable value: ``{"var-id": "val-id"}``.
        ``timing`` can be ``'realtime'``, ``'realtime_noloads'``, or ``'ingame'``.
        """
        params: dict = {
            "top": top, "platform": platform, "region": region,
            "timing": timing, "date": date,
            "embed": self._embed(embed),
        }
        if video_only:
            params["video-only"] = "yes"
        if variables:
            for var_id, val_id in variables.items():
                params[f"var-{var_id}"] = val_id
        data = self._request(f"/leaderboards/{game}/category/{category}", params)
        return Leaderboard.from_dict(data["data"], self)

    def level_leaderboard(
        self,
        game: str,
        level: str,
        category: str,
        top: Optional[int] = None,
        platform: Optional[str] = None,
        region: Optional[str] = None,
        video_only: bool = False,
        timing: Optional[str] = None,
        date: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        embed: Optional[List[str]] = None,
    ) -> Leaderboard:
        """Fetch a per-level (Individual Level) leaderboard."""
        params: dict = {
            "top": top, "platform": platform, "region": region,
            "timing": timing, "date": date,
            "embed": self._embed(embed),
        }
        if video_only:
            params["video-only"] = "yes"
        if variables:
            for var_id, val_id in variables.items():
                params[f"var-{var_id}"] = val_id
        data = self._request(f"/leaderboards/{game}/level/{level}/{category}", params)
        return Leaderboard.from_dict(data["data"], self)

    # ------------------------------------------------------------------
    # Series
    # ------------------------------------------------------------------

    def series(self, id_or_abbr: str, embed: Optional[List[str]] = None) -> Series:
        """Fetch a single series by ID or abbreviation."""
        data = self._request(f"/series/{id_or_abbr}", {"embed": self._embed(embed)})
        return Series.from_dict(data["data"], self)

    def series_list(
        self,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        moderator: Optional[str] = None,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List all series."""
        params = {
            "name": name, "abbreviation": abbreviation, "moderator": moderator,
            "embed": self._embed(embed),
            "orderby": sort_by, "direction": direction,
        }
        return self._collection("/series", lambda d, c: Series.from_dict(d, c), params)

    def series_games(
        self,
        series_id: str,
        name: Optional[str] = None,
        platform: Optional[str] = None,
        region: Optional[str] = None,
        genre: Optional[str] = None,
        developer: Optional[str] = None,
        publisher: Optional[str] = None,
        released: Optional[int] = None,
        gametype: Optional[str] = None,
        embed: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Collection:
        """List games belonging to a series."""
        params = {
            "name": name, "platform": platform, "region": region,
            "genre": genre, "developer": developer, "publisher": publisher,
            "released": released, "gametype": gametype,
            "embed": self._embed(embed),
            "orderby": sort_by, "direction": direction,
        }
        return self._collection(
            f"/series/{series_id}/games", lambda d, c: Game.from_dict(d, c), params
        )

    # ------------------------------------------------------------------
    # Platforms & Regions
    # ------------------------------------------------------------------

    def platform(self, platform_id: str) -> Platform:
        data = self._request(f"/platforms/{platform_id}")
        return Platform.from_dict(data["data"], self)

    def platforms(
        self, sort_by: Optional[str] = None, direction: Optional[str] = None
    ) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/platforms", lambda d, c: Platform.from_dict(d, c), params)

    def region(self, region_id: str) -> Region:
        data = self._request(f"/regions/{region_id}")
        return Region.from_dict(data["data"], self)

    def regions(
        self, sort_by: Optional[str] = None, direction: Optional[str] = None
    ) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/regions", lambda d, c: Region.from_dict(d, c), params)

    # ------------------------------------------------------------------
    # Notifications & Profile  (auth required)
    # ------------------------------------------------------------------

    def notifications(
        self, sort_by: Optional[str] = None, direction: Optional[str] = None
    ) -> Collection:
        """Fetch notifications for the authenticated user."""
        self._require_auth()
        params = {"orderby": sort_by, "direction": direction}
        return self._collection(
            "/notifications", lambda d, c: Notification.from_dict(d, c), params
        )

    def profile(self) -> User:
        """Fetch the authenticated user's profile."""
        self._require_auth()
        data = self._request("/profile")
        return User.from_dict(data["data"], self)

    # ------------------------------------------------------------------
    # Guests
    # ------------------------------------------------------------------

    def guest(self, name: str) -> Guest:
        """Fetch a guest by name (case-insensitive)."""
        data = self._request(f"/guests/{name}")
        return Guest.from_dict(data["data"], self)

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def variable(self, variable_id: str) -> Variable:
        """Fetch a single variable by ID."""
        data = self._request(f"/variables/{variable_id}")
        return Variable.from_dict(data["data"], self)

    # ------------------------------------------------------------------
    # Simple resources: engines, developers, publishers, gametypes, genres
    # ------------------------------------------------------------------

    def engine(self, engine_id: str) -> Engine:
        return Engine.from_dict(self._request(f"/engines/{engine_id}")["data"], self)

    def engines(self, sort_by: Optional[str] = None, direction: Optional[str] = None) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/engines", lambda d, c: Engine.from_dict(d, c), params)

    def developer(self, developer_id: str) -> Developer:
        return Developer.from_dict(self._request(f"/developers/{developer_id}")["data"], self)

    def developers(self, sort_by: Optional[str] = None, direction: Optional[str] = None) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/developers", lambda d, c: Developer.from_dict(d, c), params)

    def publisher(self, publisher_id: str) -> Publisher:
        return Publisher.from_dict(self._request(f"/publishers/{publisher_id}")["data"], self)

    def publishers(self, sort_by: Optional[str] = None, direction: Optional[str] = None) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/publishers", lambda d, c: Publisher.from_dict(d, c), params)

    def gametype(self, gametype_id: str) -> GameType:
        return GameType.from_dict(self._request(f"/gametypes/{gametype_id}")["data"], self)

    def gametypes(self, sort_by: Optional[str] = None, direction: Optional[str] = None) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/gametypes", lambda d, c: GameType.from_dict(d, c), params)

    def genre(self, genre_id: str) -> Genre:
        return Genre.from_dict(self._request(f"/genres/{genre_id}")["data"], self)

    def genres(self, sort_by: Optional[str] = None, direction: Optional[str] = None) -> Collection:
        params = {"orderby": sort_by, "direction": direction}
        return self._collection("/genres", lambda d, c: Genre.from_dict(d, c), params)
