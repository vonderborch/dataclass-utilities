from dataclasses import dataclass, fields
from typing import Dict, Optional, List


@dataclass
class MockDataclass:
    a: int
    b: Optional[str]
    c: str = "hello world"


@dataclass
class ParentMockDataclass:
    a: int
    child: MockDataclass


@dataclass
class DictParentMockDataclass:
    a: int
    child: Optional[Dict[str, Optional[MockDataclass]]]


@dataclass
class ListParentMockDataclass:
    a: int
    child: List[Optional[MockDataclass]]
