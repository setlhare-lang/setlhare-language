"""Setlhare type representations + unification.

Setlhare is progressively typed: when the checker cannot prove a type, it falls back
to ``Dyn`` rather than emitting an error. Only contradictory facts (two distinct
concrete types meeting at the same value) are errors. This keeps the language
joyful for prototypes while flagging real bugs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class Type:
    """Base class for all Setlhare types."""

    name: str = ""

    def pretty(self) -> str:
        return self.name


@dataclass(frozen=True)
class TCon(Type):
    """Concrete primitive type: Int, Float, Str, Bool, Nil."""

    name: str = ""

    def pretty(self) -> str:
        return self.name


@dataclass(frozen=True)
class TDyn(Type):
    name: str = "Dyn"

    def pretty(self) -> str:
        return "Dyn"


@dataclass(eq=False)
class TVar(Type):
    """Inference variable. Mutable so it can be substituted in place."""

    id: int = 0
    name: str = "?"

    def pretty(self) -> str:
        return f"?{self.id}"


@dataclass(frozen=True)
class TList(Type):
    elem: Type = field(default_factory=lambda: TDyn())
    name: str = "List"

    def pretty(self) -> str:
        return f"List[{self.elem.pretty()}]"


@dataclass(frozen=True)
class TDict(Type):
    key: Type = field(default_factory=lambda: TDyn())
    val: Type = field(default_factory=lambda: TDyn())
    name: str = "Dict"

    def pretty(self) -> str:
        return f"Dict[{self.key.pretty()}, {self.val.pretty()}]"


@dataclass(frozen=True)
class TSet(Type):
    elem: Type = field(default_factory=lambda: TDyn())
    name: str = "Set"

    def pretty(self) -> str:
        return f"Set[{self.elem.pretty()}]"


@dataclass(frozen=True)
class TArrow(Type):
    params: tuple[Type, ...] = ()
    ret: Type = field(default_factory=lambda: TDyn())
    name: str = "Func"

    def pretty(self) -> str:
        ps = ", ".join(p.pretty() for p in self.params)
        return f"({ps}) -> {self.ret.pretty()}"


@dataclass
class TStruct(Type):
    """Nominal struct type. Equality is by ``name`` only."""

    name: str = ""
    fields: dict[str, Type] = field(default_factory=dict)
    methods: dict[str, TArrow] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TStruct) and other.name == self.name

    def __hash__(self) -> int:
        return hash(("struct", self.name))

    def pretty(self) -> str:
        return self.name


@dataclass
class TEnum(Type):
    name: str = ""
    variants: dict[str, list[Type]] = field(default_factory=dict)
    methods: dict[str, TArrow] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TEnum) and other.name == self.name

    def __hash__(self) -> int:
        return hash(("enum", self.name))

    def pretty(self) -> str:
        return self.name


# Shared singletons.
Int = TCon("Int")
Float = TCon("Float")
Str = TCon("Str")
Bool = TCon("Bool")
Nil = TCon("Nil")
Dynamic = TDyn()
Never = TCon("Never")


# ── unification ───────────────────────────────────────────────────────


class TypeError_(Exception):
    def __init__(self, message: str, line: int = 0, col: int = 0):
        super().__init__(message)
        self.line = line
        self.col = col


_TVAR_COUNTER = [0]


def fresh_tvar(hint: str = "?") -> TVar:
    _TVAR_COUNTER[0] += 1
    return TVar(id=_TVAR_COUNTER[0], name=hint)


def reset_fresh() -> None:
    _TVAR_COUNTER[0] = 0


Subst = dict[int, Type]


def walk(t: Type, subst: Subst) -> Type:
    while isinstance(t, TVar) and t.id in subst:
        t = subst[t.id]
    return t


def occurs(var: TVar, t: Type, subst: Subst) -> bool:
    t = walk(t, subst)
    if isinstance(t, TVar):
        return t.id == var.id
    if isinstance(t, TList):
        return occurs(var, t.elem, subst)
    if isinstance(t, TDict):
        return occurs(var, t.key, subst) or occurs(var, t.val, subst)
    if isinstance(t, TSet):
        return occurs(var, t.elem, subst)
    if isinstance(t, TArrow):
        return any(occurs(var, p, subst) for p in t.params) or occurs(var, t.ret, subst)
    return False


def unify(a: Type, b: Type, subst: Subst, *, line: int = 0, col: int = 0) -> None:
    a, b = walk(a, subst), walk(b, subst)
    if isinstance(a, TDyn) or isinstance(b, TDyn):
        return
    if isinstance(a, TVar):
        if isinstance(b, TVar) and a.id == b.id:
            return
        if occurs(a, b, subst):
            raise TypeError_(f"occurs check failed: {a.pretty()} in {b.pretty()}", line, col)
        subst[a.id] = b
        return
    if isinstance(b, TVar):
        unify(b, a, subst, line=line, col=col)
        return
    if isinstance(a, TCon) and isinstance(b, TCon):
        if a.name == b.name:
            return
        raise TypeError_(f"type mismatch: {a.pretty()} vs {b.pretty()}", line, col)
    if isinstance(a, TList) and isinstance(b, TList):
        unify(a.elem, b.elem, subst, line=line, col=col)
        return
    if isinstance(a, TDict) and isinstance(b, TDict):
        unify(a.key, b.key, subst, line=line, col=col)
        unify(a.val, b.val, subst, line=line, col=col)
        return
    if isinstance(a, TSet) and isinstance(b, TSet):
        unify(a.elem, b.elem, subst, line=line, col=col)
        return
    if isinstance(a, TArrow) and isinstance(b, TArrow):
        if len(a.params) != len(b.params):
            raise TypeError_(
                f"function arity mismatch: {len(a.params)} vs {len(b.params)}", line, col
            )
        for p, q in zip(a.params, b.params, strict=True):
            unify(p, q, subst, line=line, col=col)
        unify(a.ret, b.ret, subst, line=line, col=col)
        return
    if isinstance(a, TStruct) and isinstance(b, TStruct):
        if a.name == b.name:
            return
        raise TypeError_(f"struct mismatch: {a.name} vs {b.name}", line, col)
    if isinstance(a, TEnum) and isinstance(b, TEnum):
        if a.name == b.name:
            return
        raise TypeError_(f"enum mismatch: {a.name} vs {b.name}", line, col)
    raise TypeError_(f"cannot unify {a.pretty()} with {b.pretty()}", line, col)


def apply_subst(t: Type, subst: Subst) -> Type:
    t = walk(t, subst)
    if isinstance(t, TList):
        return TList(elem=apply_subst(t.elem, subst))
    if isinstance(t, TDict):
        return TDict(key=apply_subst(t.key, subst), val=apply_subst(t.val, subst))
    if isinstance(t, TSet):
        return TSet(elem=apply_subst(t.elem, subst))
    if isinstance(t, TArrow):
        return TArrow(
            params=tuple(apply_subst(p, subst) for p in t.params),
            ret=apply_subst(t.ret, subst),
        )
    return t


def from_annotation(name: str | None) -> Type:
    """Map a textual type annotation to a Setlhare type."""
    if name is None:
        return Dynamic
    table: dict[str, Type] = {
        "int": Int,
        "Int": Int,
        "float": Float,
        "Float": Float,
        "str": Str,
        "Str": Str,
        "string": Str,
        "bool": Bool,
        "Bool": Bool,
        "nil": Nil,
        "Nil": Nil,
        "any": Dynamic,
        "Any": Dynamic,
        "Dyn": Dynamic,
    }
    return table.get(name, Dynamic)


# Allow ``isinstance`` checks while keeping Type abstractly importable.
__all__ = [
    "Bool",
    "Dynamic",
    "Float",
    "Int",
    "Never",
    "Nil",
    "Str",
    "Subst",
    "TArrow",
    "TCon",
    "TDict",
    "TDyn",
    "TEnum",
    "TList",
    "TSet",
    "TStruct",
    "TVar",
    "Type",
    "TypeError_",
    "apply_subst",
    "fresh_tvar",
    "from_annotation",
    "reset_fresh",
    "unify",
    "walk",
]


# Backward-compatible alias used by some tooling.
def is_dyn(t: Any) -> bool:
    return isinstance(t, TDyn)
