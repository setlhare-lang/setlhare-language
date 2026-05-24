# Setlhare

> **Status:** pre-alpha · spec in flux · do not depend on this yet

Setlhare is a programming language under active design. The goal is
Python-grade ergonomics with Rust-grade safety, expressed in a grammar
that borrows from Setswana storytelling.

This repository is the canonical implementation: compiler, runtime,
standard library, package manager (`spore`), language server, and
tree-sitter grammar.

---

## What works today (v0.1, pre-alpha)

- Hand-written lexer
- Hand-written recursive-descent parser → AST
- AST-walking interpreter (functions, closures, loops, conditionals,
  `match`, collections, imports, `Result`/`?`, `spawn`/`go`)
- Runtime with immutable-binding enforcement
- 16 standard-library modules (`io`, `math`, `text`, `time`, `fs`,
  `http`, `json`, `result`, `collections`, `crypto`, `ml`, `quantum`,
  `embed`, `actors`, ...) — implementations in Python, public API surfaces only
- Skeletons (not production) for: type checker, borrow checker,
  bytecode emitter, WASM backend, LLVM backend, LSP, `spore`

## What does NOT work yet

- Static typing is not enforced (skeleton only)
- Borrow checking is not enforced (skeleton only)
- WASM and LLVM backends do not emit usable binaries
- Tree-sitter grammar does not exist yet
- The language specification (`docs/spec/`) is being written

See `docs/spec/00-overview.md` for the design north star.

---

## Quickstart

Requires Python ≥ 3.11.

```bash
git clone https://github.com/setlhare-lang/setlhare.git
cd setlhare
pip install -e ".[dev]"

setlhare run examples/hello.sl
setlhare check examples/hello.sl
pytest -q
```

Or open the repo in a GitHub Codespace / VS Code Dev Container — the
`.devcontainer/` provides Python, LLVM, Binaryen/WABT, Node, and
tree-sitter pre-installed.

---

## Example

```setlhare
func square(n: int) -> int => n * n

func main() {
    name := "Setlhare"
    nums := [1, 2, 3, 4]
    print("Dumela, #{name}!")
    print(nums.filter(is_even).map(square).sum())
}
```

---

## Repository layout

```
setlhare-lang/setlhare
├── setlhare/             # the implementation
│   ├── lexer/            # tokens, lexer
│   ├── parser/           # AST, recursive-descent parser
│   ├── compiler/         # hir, mir, typecheck, borrow, codegen
│   ├── runtime/          # tree-walking interpreter
│   ├── stdlib/           # standard library (Python-backed)
│   ├── tools/            # spore (pkg mgr), lsp
│   ├── cli.py            # `setlhare` entrypoint
│   └── errors.py
├── grammar/
│   └── tree-sitter-setlhare/   # formal grammar (v0.7)
├── tools/
│   └── vscode-setlhare/  # VS Code extension
├── std/                  # stdlib written in Setlhare (.sl) — v0.3+
├── examples/             # *.sl example programs
├── tests/                # pytest + conformance suite
├── docs/
│   ├── spec/             # ← the language specification (source of truth)
│   ├── language.md       # user-facing tutorial (in progress)
│   ├── compiler-roadmap.md
│   └── production-readiness.md
├── .devcontainer/
└── .github/
```

---

## Milestones

| Version | Theme |
|---------|-------|
| **v0.1** | Parser + interpreter + spec draft *(current)* |
| **v0.2** | MIR + bytecode VM |
| **v0.3** | Static type checker (enforced) |
| **v0.4** | Ownership / borrow checker (enforced) |
| **v0.5** | Structs, enums, traits, generics stable |
| **v0.6** | `spore` package manager |
| **v0.7** | LSP + formatter + tree-sitter grammar |
| **v0.8** | WASM backend |
| **v0.9** | LLVM backend |
| **v1.0** | Stability + conformance suite + docs |

Track progress on the [GitHub milestones page](https://github.com/setlhare-lang/setlhare/milestones).

---

## Contributing

This is a young project. We need help — see [CONTRIBUTING.md](CONTRIBUTING.md).

Roles we're recruiting:

- Compiler engineer (IR, codegen)
- Type-systems engineer (typecheck, traits, generics)
- Runtime / VM engineer (bytecode interpreter, GC, actors)
- Tooling engineer (LSP, formatter, tree-sitter)
- Docs & conformance test engineer

If you want to discuss the language design before writing code, open a
**Spec RFC** issue.

---

## License

Apache-2.0 © The Setlhare Authors. See [LICENSE](LICENSE).
