from __future__ import annotations


class SetlhareError(Exception):
    """Base error for Setlhare tooling."""


class SetlhareSyntaxError(SetlhareError):
    pass


class SetlhareRuntimeError(SetlhareError):
    pass


class ImmutableAssignmentError(SetlhareRuntimeError):
    pass


def format_source_context(
    source: str, line: int, col: int, *, filename: str = "<source>", context: int = 1
) -> str:
    """Render a snippet with a caret pointing at the error location.

    Format mirrors Rust / Elm: a header, the offending line, and a caret column.
    """
    if not source:
        return f"  --> {filename}:{line}:{col}"
    lines = source.splitlines()
    if line < 1 or line > len(lines):
        return f"  --> {filename}:{line}:{col}"
    out: list[str] = [f"  --> {filename}:{line}:{col}"]
    start = max(1, line - context)
    end = min(len(lines), line + context)
    width = len(str(end))
    for ln in range(start, end + 1):
        marker = " | "
        out.append(f"  {ln:>{width}}{marker}{lines[ln - 1]}")
        if ln == line:
            caret_pad = " " * (col - 1)
            out.append(f"  {' ' * width}{marker}{caret_pad}^")
    return "\n".join(out)
