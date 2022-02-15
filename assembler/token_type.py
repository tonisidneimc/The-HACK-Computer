from typing import NamedTuple

__all__ = ["Token"]

class Token(NamedTuple):
    type: str
    value: str
    lineno: int
    column: int
    