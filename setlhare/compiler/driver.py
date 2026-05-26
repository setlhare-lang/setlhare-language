from __future__ import annotations

import pathlib
from typing import Protocol

from setlhare.parser.parser import Parser

from .borrow import BorrowChecker
from .bytecode import BytecodeBackend
from .llvm_backend import LLVMBackend
from .typechecker import TypeChecker
from .wasm_backend import WasmBackend


class Backend(Protocol):
    def emit(self, module): ...


BACKENDS: dict[str, type[Backend]] = {
    "bytecode": BytecodeBackend,
    "llvm": LLVMBackend,
    "wasm": WasmBackend,
}


def compile_file(path: pathlib.Path, target="bytecode", emit=False):
    source = path.read_text(encoding="utf-8")
    module = Parser().parse(source, str(path))
    types = TypeChecker().check(module, source=source, filename=str(path))
    BorrowChecker().check(module)
    artifact = BACKENDS[target]().emit(module)
    if emit:
        suffix = {"bytecode": ".slbc", "llvm": ".ll", "wasm": ".wat"}[target]
        out = path.with_suffix(suffix)
        out.write_text(str(artifact), encoding="utf-8")
        print(f"wrote {out}")
    else:
        print("check ok")
        for name, typ in sorted(types.items()):
            print(f"  {name}: {typ.pretty()}")
    return artifact
