from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import Link, parse_links


@dataclass
class VariableValue:
    id: str
    label: str
    rules: Optional[str] = None
    miscellaneous: Optional[bool] = None


@dataclass
class VariableScope:
    type: str  # 'global', 'full-game', 'all-levels', 'single-level'
    level_id: Optional[str] = None


@dataclass
class Variable:
    id: str
    name: str
    scope: VariableScope
    mandatory: bool
    user_defined: bool
    obsoletes: bool
    values: Dict[str, VariableValue]
    category_id: Optional[str] = None
    default_value: Optional[str] = None
    links: List[Link] = field(default_factory=list)
    _client: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, d: dict, client: Any = None) -> "Variable":
        scope_data = d.get("scope", {})
        scope = VariableScope(
            type=scope_data.get("type", "global"),
            level_id=scope_data.get("level"),
        )

        values_container = d.get("values", {})
        raw_values = values_container.get("values", {})
        values: Dict[str, VariableValue] = {}
        for vid, vdata in raw_values.items():
            flags = vdata.get("flags") or {}
            values[vid] = VariableValue(
                id=vid,
                label=vdata.get("label", ""),
                rules=vdata.get("rules"),
                miscellaneous=flags.get("miscellaneous"),
            )

        return cls(
            id=d["id"],
            name=d["name"],
            scope=scope,
            mandatory=d.get("mandatory", False),
            user_defined=d.get("user-defined", False),
            obsoletes=d.get("obsoletes", True),
            values=values,
            category_id=d.get("category"),
            default_value=values_container.get("default"),
            links=parse_links(d.get("links")),
            _client=client,
        )
