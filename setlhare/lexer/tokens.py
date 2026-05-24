from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

KEYWORDS = {
    "func", "struct", "actor", "trait", "match", "case", "if", "elif", "else",
    "for", "while", "in", "return", "break", "continue", "spawn", "go", "mut",
    "import", "enum", "macro", "true", "false", "nil", "and", "or", "not"
}

@dataclass(frozen=True, slots=True)
class SourcePos:
    line: int
    col: int

@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    value: str
    line: int
    col: int

    @property
    def pos(self) -> SourcePos:
        return SourcePos(self.line, self.col)
