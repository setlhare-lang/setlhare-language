from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    name: str


Int = Type("Int")
Float = Type("Float")
Str = Type("Str")
Bool = Type("Bool")
Dynamic = Type("Dyn")
Never = Type("Never")
