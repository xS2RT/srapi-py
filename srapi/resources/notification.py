from dataclasses import dataclass, field
from typing import Any, List

from ..types import Link, parse_links


@dataclass
class NotificationItem:
    type: str   # 'post', 'run', 'game', 'guide'
    uri: str


@dataclass
class Notification:
    id: str
    created: str
    status: str  # 'read' or 'unread'
    text: str
    item: NotificationItem
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Notification":
        item_data = d.get("item", {})
        item = NotificationItem(
            type=item_data.get("rel", ""),
            uri=item_data.get("uri", ""),
        )
        return cls(
            id=d["id"],
            created=d.get("created", ""),
            status=d.get("status", ""),
            text=d.get("text", ""),
            item=item,
            links=parse_links(d.get("links")),
            _client=client,
        )
