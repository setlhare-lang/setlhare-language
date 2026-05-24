from __future__ import annotations
from setlhare.parser import ast as A

class BorrowChecker:
    """Early ownership/immutability pass.

    This enforces implemented Setlhare guarantees now and is structured for the future
    move/borrow/lifetime region solver.
    """
    def check(self, module: A.Module) -> None:
        self.immutable: set[str] = set()
        for node in module.body:
            self._visit(node)

    def _visit(self, node) -> None:
        if isinstance(node, A.Binding):
            if node.name in self.immutable:
                raise RuntimeError(f"cannot rebind immutable binding '{node.name}' at {node.line}:{node.col}")
            if not node.mutable:
                self.immutable.add(node.name)
        elif isinstance(node, A.Assign):
            if node.name in self.immutable:
                raise RuntimeError(f"cannot assign to immutable binding '{node.name}' at {node.line}:{node.col}")
        elif isinstance(node, A.Function):
            self.immutable.add(node.name)
        elif isinstance(node, A.If):
            for s in (node.then_block.statements if node.then_block else []): self._visit(s)
            for _, b in node.elifs:
                for s in b.statements: self._visit(s)
            if node.else_block:
                for s in node.else_block.statements: self._visit(s)
        elif isinstance(node, (A.While, A.For)):
            for s in (node.body.statements if node.body else []): self._visit(s)
