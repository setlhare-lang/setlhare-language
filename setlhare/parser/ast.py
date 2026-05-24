from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Node:
    line: int = 0
    col: int = 0


@dataclass(slots=True)
class Module(Node):
    body: list[Any] = field(default_factory=list)


@dataclass(slots=True)
class Block(Node):
    statements: list[Any] = field(default_factory=list)


@dataclass(slots=True)
class Function(Node):
    name: str = ""
    params: list[str] = field(default_factory=list)
    body: Block | None = None
    return_type: str | None = None


@dataclass(slots=True)
class Binding(Node):
    name: str = ""
    value: Any = None
    mutable: bool = True
    type_name: str | None = None


@dataclass(slots=True)
class Assign(Node):
    name: str = ""
    value: Any = None


@dataclass(slots=True)
class If(Node):
    condition: Any = None
    then_block: Block | None = None
    elifs: list[tuple[Any, Block]] = field(default_factory=list)
    else_block: Block | None = None


@dataclass(slots=True)
class While(Node):
    condition: Any = None
    body: Block | None = None


@dataclass(slots=True)
class For(Node):
    name: str = ""
    iterable: Any = None
    body: Block | None = None


@dataclass(slots=True)
class Return(Node):
    value: Any = None


@dataclass(slots=True)
class Break(Node):
    pass


@dataclass(slots=True)
class Continue(Node):
    pass


@dataclass(slots=True)
class Import(Node):
    module: str = ""


@dataclass(slots=True)
class ExprStmt(Node):
    expr: Any = None


@dataclass(slots=True)
class MatchCase(Node):
    pattern: Any = None
    body: Block | None = None
    is_wildcard: bool = False


@dataclass(slots=True)
class Match(Node):
    value: Any = None
    cases: list[MatchCase] = field(default_factory=list)


@dataclass(slots=True)
class Literal(Node):
    value: Any = None
    raw: str | None = None


@dataclass(slots=True)
class Name(Node):
    name: str = ""


@dataclass(slots=True)
class ListExpr(Node):
    items: list[Any] = field(default_factory=list)


@dataclass(slots=True)
class DictExpr(Node):
    items: list[tuple[Any, Any]] = field(default_factory=list)


@dataclass(slots=True)
class SetExpr(Node):
    items: list[Any] = field(default_factory=list)


@dataclass(slots=True)
class Unary(Node):
    op: str = ""
    right: Any = None


@dataclass(slots=True)
class Binary(Node):
    left: Any = None
    op: str = ""
    right: Any = None


@dataclass(slots=True)
class Call(Node):
    callee: Any = None
    args: list[Any] = field(default_factory=list)


@dataclass(slots=True)
class GetAttr(Node):
    obj: Any = None
    name: str = ""


@dataclass(slots=True)
class Index(Node):
    obj: Any = None
    index: Any = None


@dataclass(slots=True)
class ResultUnwrap(Node):
    expr: Any = None


@dataclass(slots=True)
class Spawn(Node):
    call: Call | None = None
    kind: str = "spawn"


# Backward-compatible wrapper used by older compiler code paths.
@dataclass(slots=True)
class Expr(Node):
    source: str = ""
