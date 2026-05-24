from __future__ import annotations

from dataclasses import dataclass

from setlhare.errors import SetlhareRuntimeError
from setlhare.parser import ast as A

from .types import Bool, Dynamic, Float, Int, Str, Type


@dataclass(slots=True)
class Diagnostic:
    severity: str
    message: str
    line: int = 0
    col: int = 0


class TypeChecker:
    """Conservative MVP type checker.

    It performs real symbol tracking and literal/operator inference, while falling back to
    Dynamic for values that require the future Hindley-Milner/trait solver.
    """

    def __init__(self):
        self.env: dict[str, Type] = {}
        self.immutable: set[str] = set()
        self.diagnostics: list[Diagnostic] = []

    def check(self, module: A.Module) -> dict[str, Type]:
        for node in module.body:
            self.visit(node)
        return self.env

    def visit(self, node):
        if isinstance(node, A.Import):
            self.env[node.module.split("::")[-1]] = Dynamic
        elif isinstance(node, A.Function):
            self.env[node.name] = Dynamic
            self.immutable.add(node.name)
        elif isinstance(node, A.Binding):
            self.env[node.name] = self.infer(node.value)
            if not node.mutable:
                self.immutable.add(node.name)
        elif isinstance(node, A.Assign):
            if node.name in self.immutable:
                self.diagnostics.append(
                    Diagnostic(
                        "error",
                        f"cannot assign to immutable binding '{node.name}'",
                        node.line,
                        node.col,
                    )
                )
            self.env[node.name] = self.infer(node.value)
        elif isinstance(node, A.If):
            self.infer(node.condition)
            for s in node.then_block.statements if node.then_block else []:
                self.visit(s)
            for _, b in node.elifs:
                for s in b.statements:
                    self.visit(s)
            if node.else_block:
                for s in node.else_block.statements:
                    self.visit(s)
        elif isinstance(node, (A.While, A.For)):
            for s in node.body.statements if node.body else []:
                self.visit(s)
        elif isinstance(node, A.Return) and node.value is not None:
            self.infer(node.value)
        elif isinstance(node, A.ExprStmt):
            self.infer(node.expr)
        if self.diagnostics:
            first = self.diagnostics[0]
            raise SetlhareRuntimeError(
                f"type check failed: {first.message} at {first.line}:{first.col}"
            )

    def infer(self, expr) -> Type:
        if isinstance(expr, A.Literal):
            if isinstance(expr.value, bool):
                return Bool
            if isinstance(expr.value, int):
                return Int
            if isinstance(expr.value, float):
                return Float
            if isinstance(expr.value, str):
                return Str
            return Dynamic
        if isinstance(expr, A.Name):
            return self.env.get(expr.name, Dynamic)
        if isinstance(expr, A.Binary):
            lt, rt = self.infer(expr.left), self.infer(expr.right)
            if expr.op in {"==", "!=", "<", "<=", ">", ">=", "and", "or"}:
                return Bool
            if lt is Float or rt is Float:
                return Float
            if lt is Int and rt is Int:
                return Int
            if expr.op == "+" and lt is Str and rt is Str:
                return Str
            return Dynamic
        if isinstance(expr, A.Unary):
            return Bool if expr.op in {"!", "not"} else self.infer(expr.right)
        if isinstance(
            expr,
            (
                A.Call,
                A.GetAttr,
                A.Index,
                A.ResultUnwrap,
                A.Spawn,
                A.ListExpr,
                A.DictExpr,
                A.SetExpr,
            ),
        ):
            return Dynamic
        return Dynamic
