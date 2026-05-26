"""Setlhare progressive static type checker.

Implements a Hindley-Milner-style constraint-based inference engine relaxed for
progressive typing: the special ``Dyn`` type unifies with anything and silences
errors. Concrete contradictions still fail loudly with a source-context snippet.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass

from setlhare.errors import SetlhareError, format_source_context
from setlhare.parser import ast as A

from .types import (
    Bool,
    Dynamic,
    Float,
    Int,
    Nil,
    Str,
    Subst,
    TArrow,
    TDict,
    TEnum,
    TList,
    TSet,
    TStruct,
    Type,
    TypeError_,
    apply_subst,
    fresh_tvar,
    from_annotation,
    reset_fresh,
    unify,
)


class SetlhareTypeError(SetlhareError):
    """Raised when type checking finds a contradiction."""


@dataclass(slots=True)
class Diagnostic:
    severity: str
    message: str
    line: int = 0
    col: int = 0


class TypeEnv:
    """Lexically scoped name → Type bindings."""

    def __init__(self, parent: TypeEnv | None = None) -> None:
        self.parent = parent
        self.values: dict[str, Type] = {}
        self.immutable: set[str] = set()

    def define(self, name: str, t: Type, *, mutable: bool = True) -> None:
        self.values[name] = t
        if not mutable:
            self.immutable.add(name)

    def assign(self, name: str, t: Type) -> TypeEnv | None:
        env = self._find(name)
        if env is None:
            self.define(name, t)
            return self
        env.values[name] = t
        return env

    def lookup(self, name: str) -> Type | None:
        env = self._find(name)
        return env.values[name] if env is not None else None

    def is_immutable(self, name: str) -> bool:
        env = self._find(name)
        return env is not None and name in env.immutable

    def _find(self, name: str) -> TypeEnv | None:
        if name in self.values:
            return self
        return self.parent._find(name) if self.parent else None


_BUILTIN_NAMES = {
    "print": TArrow(params=(Dynamic,), ret=Nil),
    "input": TArrow(params=(Dynamic,), ret=Str),
    "len": TArrow(params=(Dynamic,), ret=Int),
    # range supports range(stop), range(start, stop), and range(start, stop, step) — keep dynamic.
    "range": Dynamic,
    "int": TArrow(params=(Dynamic,), ret=Int),
    "float": TArrow(params=(Dynamic,), ret=Float),
    "str": TArrow(params=(Dynamic,), ret=Str),
    "bool": TArrow(params=(Dynamic,), ret=Bool),
    "list": TArrow(params=(Dynamic,), ret=TList(elem=Dynamic)),
    "dict": TArrow(params=(), ret=TDict()),
    "set": TArrow(params=(Dynamic,), ret=TSet()),
    "Ok": TArrow(params=(Dynamic,), ret=Dynamic),
    "Err": TArrow(params=(Dynamic,), ret=Dynamic),
    "spawn": Dynamic,
    "go": Dynamic,
    "true": Bool,
    "false": Bool,
    "nil": Nil,
}


class TypeChecker:
    """Constraint-based progressive type checker."""

    def __init__(self) -> None:
        self.subst: Subst = {}
        self.diagnostics: list[Diagnostic] = []
        self.source: str = ""
        self.filename: str = "<source>"

    # ── public API ────────────────────────────────────────────────────

    def check(
        self, module: A.Module, *, source: str = "", filename: str = "<source>"
    ) -> dict[str, Type]:
        reset_fresh()
        self.source = source
        self.filename = filename
        self.diagnostics.clear()
        env = TypeEnv()
        for name, t in _BUILTIN_NAMES.items():
            env.define(name, t, mutable=False)
        # First pass: hoist top-level declarations so they can refer to each other.
        self._hoist(module.body, env)
        # Second pass: infer bodies and statements in source order.
        for stmt in module.body:
            self._stmt(stmt, env)
        if self.diagnostics:
            d = self.diagnostics[0]
            snippet = format_source_context(self.source, d.line, d.col, filename=self.filename)
            raise SetlhareTypeError(f"{d.message}\n{snippet}")
        return {n: apply_subst(t, self.subst) for n, t in env.values.items()}

    # ── declaration hoisting ──────────────────────────────────────────

    def _hoist(self, body: list, env: TypeEnv) -> None:
        for node in body:
            if isinstance(node, A.StructDecl):
                env.define(
                    node.name,
                    TStruct(
                        name=node.name,
                        fields={f: fresh_tvar(f) for f in node.fields},
                    ),
                    mutable=False,
                )
            elif isinstance(node, A.EnumDecl):
                env.define(
                    node.name,
                    TEnum(
                        name=node.name,
                        variants={v.name: [fresh_tvar(f) for f in v.fields] for v in node.variants},
                    ),
                    mutable=False,
                )
            elif isinstance(node, A.Function):
                params = tuple(fresh_tvar(p) for p in node.params)
                ret = fresh_tvar("ret")
                env.define(node.name, TArrow(params=params, ret=ret), mutable=False)

    # ── statements ────────────────────────────────────────────────────

    def _stmt(self, node, env: TypeEnv) -> None:
        if isinstance(node, A.Import):
            env.define(node.module.split("::")[-1], Dynamic, mutable=False)
            return
        if isinstance(node, A.Function):
            self._function(node, env)
            return
        if isinstance(node, A.StructDecl):
            return
        if isinstance(node, A.EnumDecl):
            return
        if isinstance(node, A.ImplBlock):
            self._impl(node, env)
            return
        if isinstance(node, A.Binding):
            declared = from_annotation(node.type_name) if node.type_name else None
            inferred = self._expr(node.value, env)
            if declared is not None:
                self._unify(declared, inferred, node)
                env.define(node.name, declared, mutable=node.mutable)
            else:
                env.define(node.name, inferred, mutable=node.mutable)
            return
        if isinstance(node, A.Assign):
            if env.is_immutable(node.name):
                self._diag(
                    f"cannot assign to immutable binding '{node.name}'",
                    node.line,
                    node.col,
                )
                return
            existing = env.lookup(node.name)
            value_t = self._expr(node.value, env)
            if existing is not None:
                self._unify(existing, value_t, node)
            else:
                env.assign(node.name, value_t)
            return
        if isinstance(node, A.IndexAssign):
            self._expr(node.target, env)
            self._expr(node.value, env)
            return
        if isinstance(node, A.AttrAssign):
            self._expr(node.target, env)
            self._expr(node.value, env)
            return
        if isinstance(node, A.If):
            self._unify(self._expr(node.condition, env), Bool, node)
            self._block(node.then_block, env)
            for cond, block in node.elifs:
                self._unify(self._expr(cond, env), Bool, node)
                self._block(block, env)
            if node.else_block:
                self._block(node.else_block, env)
            return
        if isinstance(node, A.While):
            self._unify(self._expr(node.condition, env), Bool, node)
            self._block(node.body, env)
            return
        if isinstance(node, A.For):
            iter_t = self._expr(node.iterable, env)
            elem = fresh_tvar("elem")
            # Allow list/range/dyn iteration.
            with contextlib.suppress(TypeError_):
                unify(iter_t, TList(elem=elem), self.subst, line=node.line, col=node.col)
            loop_env = TypeEnv(env)
            loop_env.define(node.name, elem)
            self._block(node.body, loop_env)
            return
        if isinstance(node, A.Match):
            scrutinee = self._expr(node.value, env)
            for case in node.cases:
                case_env = TypeEnv(env)
                self._bind_pattern(case, scrutinee, case_env)
                self._block(case.body, case_env)
            return
        if isinstance(node, A.Return):
            if node.value is not None:
                self._expr(node.value, env)
            return
        if isinstance(node, (A.Break, A.Continue)):
            return
        if isinstance(node, A.ExprStmt):
            self._expr(node.expr, env)
            return
        # Unknown statement kinds: silently ignore so checker stays robust.

    def _bind_pattern(self, case: A.MatchCase, scrutinee: Type, env: TypeEnv) -> None:
        """Introduce names from a pattern into the case environment."""
        pattern = case.pattern
        if not isinstance(pattern, A.VariantPattern):
            return
        head = env.lookup(pattern.type_name)
        if isinstance(scrutinee, TEnum) and head is None:
            head = scrutinee
        payload_types: list[Type]
        if isinstance(head, TEnum) and pattern.variant in head.variants:
            payload_types = list(head.variants[pattern.variant])
        else:
            payload_types = [Dynamic] * len(pattern.bindings)
        for binding, ptype in zip(pattern.bindings, payload_types, strict=False):
            if binding is not None:
                env.define(binding, ptype)

    def _block(self, block: A.Block | None, env: TypeEnv) -> None:
        if block is None:
            return
        local = TypeEnv(env)
        for stmt in block.statements:
            self._stmt(stmt, local)

    # ── functions & impls ─────────────────────────────────────────────

    def _function(self, node: A.Function, env: TypeEnv, *, receiver: Type | None = None) -> TArrow:
        # Recover the hoisted arrow if present so recursion lines up.
        existing = env.lookup(node.name)
        if isinstance(existing, TArrow) and len(existing.params) == len(node.params):
            arrow = existing
        else:
            arrow = TArrow(
                params=tuple(fresh_tvar(p) for p in node.params),
                ret=fresh_tvar("ret"),
            )
            env.define(node.name, arrow, mutable=False)

        body_env = TypeEnv(env)
        for pname, ptype in zip(node.params, arrow.params, strict=True):
            body_env.define(pname, ptype)
        if receiver is not None:
            body_env.define("self", receiver, mutable=False)
        self._block(node.body, body_env)
        return arrow

    def _impl(self, node: A.ImplBlock, env: TypeEnv) -> None:
        target = env.lookup(node.target)
        if not isinstance(target, (TStruct, TEnum)):
            self._diag(
                f"impl target '{node.target}' is not a struct or enum",
                node.line,
                node.col,
            )
            return
        for method in node.methods:
            arrow = TArrow(
                params=tuple(fresh_tvar(p) for p in method.params),
                ret=fresh_tvar("ret"),
            )
            method_env = TypeEnv(env)
            method_env.define(method.name, arrow, mutable=False)
            for pname, ptype in zip(method.params, arrow.params, strict=True):
                method_env.define(pname, ptype)
            method_env.define("self", target, mutable=False)
            self._block(method.body, method_env)
            target.methods[method.name] = arrow

    # ── expressions ───────────────────────────────────────────────────

    def _expr(self, node, env: TypeEnv) -> Type:
        if isinstance(node, A.Literal):
            v = node.value
            if isinstance(v, bool):
                return Bool
            if isinstance(v, int):
                return Int
            if isinstance(v, float):
                return Float
            if isinstance(v, str):
                return Str
            if v is None:
                return Nil
            return Dynamic
        if isinstance(node, A.Name):
            t = env.lookup(node.name)
            if t is None:
                self._diag(f"undefined name '{node.name}'", node.line, node.col)
                return Dynamic
            return t
        if isinstance(node, A.ListExpr):
            elem = fresh_tvar("elem")
            for item in node.items:
                self._unify(elem, self._expr(item, env), node)
            return TList(elem=elem)
        if isinstance(node, A.SetExpr):
            elem = fresh_tvar("elem")
            for item in node.items:
                self._unify(elem, self._expr(item, env), node)
            return TSet(elem=elem)
        if isinstance(node, A.DictExpr):
            key = fresh_tvar("k")
            val = fresh_tvar("v")
            for k, v in node.items:
                self._unify(key, self._expr(k, env), node)
                self._unify(val, self._expr(v, env), node)
            return TDict(key=key, val=val)
        if isinstance(node, A.Unary):
            inner = self._expr(node.right, env)
            if node.op in {"!", "not"}:
                return Bool
            if node.op == "-":
                return inner
            return Dynamic
        if isinstance(node, A.Binary):
            lt = self._expr(node.left, env)
            rt = self._expr(node.right, env)
            return self._binary(node.op, lt, rt, node)
        if isinstance(node, A.Call):
            callee_t = self._expr(node.callee, env)
            arg_types = [self._expr(a, env) for a in node.args]
            ret = fresh_tvar("ret")
            if isinstance(callee_t, TArrow) and len(callee_t.params) != len(arg_types):
                # Soft warning — helps catch arity mistakes early.
                self._diag(
                    f"function expects {len(callee_t.params)} args, got {len(arg_types)}",
                    node.line,
                    node.col,
                )
                return Dynamic
            self._unify(callee_t, TArrow(params=tuple(arg_types), ret=ret), node)
            return ret
        if isinstance(node, A.GetAttr):
            obj_t = self._expr(node.obj, env)
            obj_t = apply_subst(obj_t, self.subst)
            if isinstance(obj_t, TStruct):
                if node.name in obj_t.fields:
                    return obj_t.fields[node.name]
                if node.name in obj_t.methods:
                    arrow = obj_t.methods[node.name]
                    # Drop the `self` parameter (already bound).
                    return TArrow(params=arrow.params[1:], ret=arrow.ret)
                self._diag(
                    f"struct '{obj_t.name}' has no field or method '{node.name}'",
                    node.line,
                    node.col,
                )
                return Dynamic
            if isinstance(obj_t, TEnum) and node.name in obj_t.methods:
                arrow = obj_t.methods[node.name]
                return TArrow(params=arrow.params[1:], ret=arrow.ret)
            return Dynamic
        if isinstance(node, A.Index):
            obj_t = apply_subst(self._expr(node.obj, env), self.subst)
            self._expr(node.index, env)
            if isinstance(obj_t, TList):
                return obj_t.elem
            if isinstance(obj_t, TDict):
                return obj_t.val
            return Dynamic
        if isinstance(node, A.StructLit):
            target = env.lookup(node.type_name)
            if not isinstance(target, TStruct):
                self._diag(f"'{node.type_name}' is not a struct", node.line, node.col)
                return Dynamic
            for fname, value in node.fields:
                if fname not in target.fields:
                    self._diag(
                        f"struct '{target.name}' has no field '{fname}'",
                        node.line,
                        node.col,
                    )
                    continue
                self._unify(target.fields[fname], self._expr(value, env), node)
            return target
        if isinstance(node, A.Path):
            head = env.lookup(node.parts[0])
            if isinstance(head, TEnum) and len(node.parts) == 2:
                variant = node.parts[1]
                if variant not in head.variants:
                    self._diag(
                        f"enum '{head.name}' has no variant '{variant}'",
                        node.line,
                        node.col,
                    )
                    return Dynamic
                fields = head.variants[variant]
                if not fields:
                    return head
                return TArrow(params=tuple(fields), ret=head)
            return Dynamic
        if isinstance(node, A.ResultUnwrap):
            self._expr(node.expr, env)
            return Dynamic
        if isinstance(node, A.Spawn):
            if node.call is not None:
                self._expr(node.call, env)
            return Dynamic
        return Dynamic

    # ── helpers ───────────────────────────────────────────────────────

    def _binary(self, op: str, lt: Type, rt: Type, node) -> Type:
        if op in {"==", "!=", "<", "<=", ">", ">=", "and", "or"}:
            return Bool
        if op == "+":
            # String + String → String, otherwise numeric.
            la = apply_subst(lt, self.subst)
            ra = apply_subst(rt, self.subst)
            if la == Str and ra == Str:
                return Str
            return self._numeric(lt, rt, node)
        if op in {"-", "*", "/", "%"}:
            return self._numeric(lt, rt, node)
        return Dynamic

    def _numeric(self, lt: Type, rt: Type, node) -> Type:
        la = apply_subst(lt, self.subst)
        ra = apply_subst(rt, self.subst)
        if la == Float or ra == Float:
            return Float
        if la == Int and ra == Int:
            return Int
        # Otherwise leave as Dyn (progressive typing tolerates unknowns).
        return Dynamic

    def _unify(self, a: Type, b: Type, node) -> None:
        try:
            unify(a, b, self.subst, line=getattr(node, "line", 0), col=getattr(node, "col", 0))
        except TypeError_ as exc:
            self._diag(str(exc), exc.line, exc.col)

    def _diag(self, message: str, line: int, col: int) -> None:
        self.diagnostics.append(Diagnostic("error", message, line, col))
