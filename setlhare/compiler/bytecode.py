from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Instruction:
    op: str
    arg: object = None

class BytecodeBackend:
    def emit(self, module) -> list[Instruction]:
        return [Instruction("MODULE", module), Instruction("HALT")]
