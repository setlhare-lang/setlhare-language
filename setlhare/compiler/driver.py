from __future__ import annotations
import pathlib
from setlhare.parser.parser import Parser
from .borrow import BorrowChecker
from .typechecker import TypeChecker
from .bytecode import BytecodeBackend
from .llvm_backend import LLVMBackend
from .wasm_backend import WasmBackend

BACKENDS = {"bytecode": BytecodeBackend, "llvm": LLVMBackend, "wasm": WasmBackend}

def compile_file(path: pathlib.Path, target="bytecode", emit=False):
    source = path.read_text(encoding="utf-8")
    module = Parser().parse(source)
    types = TypeChecker().check(module)
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
            print(f"  {name}: {typ.name}")
    return artifact
