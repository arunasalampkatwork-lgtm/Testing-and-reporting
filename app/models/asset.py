from dataclasses import dataclass
from typing import Optional


@dataclass
class AssetNode:

    node_id: str
    name: str
    node_type: str
    parent_id: Optional[str] = None