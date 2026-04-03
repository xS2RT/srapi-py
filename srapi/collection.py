from typing import Any, Callable, Generic, Iterator, List, Optional, TypeVar

T = TypeVar("T")


class Collection(Generic[T]):
    """A lazily-paginated collection of API resources.

    Iterating this object automatically fetches all pages. Use `.first()` to
    fetch only the first item without loading the whole collection, or
    `.all()` to eagerly collect everything into a list.
    """

    def __init__(
        self,
        client: Any,
        path: str,
        params: dict,
        parse_fn: Callable[[dict, Any], T],
        max_per_page: int = 200,
    ):
        self._client = client
        self._path = path
        self._params = params
        self._parse_fn = parse_fn
        self._max_per_page = max_per_page

    def __iter__(self) -> Iterator[T]:
        params = {**self._params, "max": self._max_per_page, "offset": 0}
        while True:
            response = self._client._request(self._path, params)
            items = response.get("data", [])
            if not items:
                break
            for item in items:
                yield self._parse_fn(item, self._client)
            pagination = response.get("pagination", {})
            links = {l["rel"]: l["uri"] for l in pagination.get("links", [])}
            if "next" not in links:
                break
            params = {**params, "offset": params["offset"] + len(items)}

    def first(self) -> Optional[T]:
        """Return the first item, fetching only one page."""
        for item in self:
            return item
        return None

    def all(self) -> List[T]:
        """Eagerly fetch all pages and return a list."""
        return list(self)

    def __repr__(self) -> str:
        return f"Collection(path={self._path!r})"
