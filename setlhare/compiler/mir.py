"""Mid-level Intermediate Representation (MIR).

MIR is a control-flow-graph (CFG) based, typed IR suitable for:
  - borrow checking (after typechecking)
  - optimization passes
  - codegen targets (bytecode VM, WASM, LLVM)

Status: PLACEHOLDER (v0.2 milestone)
Spec:   docs/spec/04-ownership.md (borrow checking operates on MIR)
"""

from __future__ import annotations

# TODO(v0.2): Define basic blocks, statements, terminators, places, rvalues.
# TODO(v0.2): HIR -> MIR lowering.
