
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Dataclass(Protocol):
    """A typing hint for checking for any dataclass."""
