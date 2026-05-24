"""Minimal LSP skeleton for Setlhare.

Next steps: speak JSON-RPC over stdin/stdout, publish diagnostics from Lexer/Parser,
serve completion items for keywords/std modules, and go-to-definition via symbol tables.
"""
KEYWORDS = ["func", "struct", "actor", "trait", "match", "spawn", "go", "mut", "import"]

def completions(prefix=""):
    return [k for k in KEYWORDS if k.startswith(prefix)]
