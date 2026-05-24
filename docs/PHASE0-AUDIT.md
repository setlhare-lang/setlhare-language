# Phase 0 Audit — 2026-05-24

Snapshot of the repository state before the first git commit.

## Removed

| Path | Reason |
|------|--------|
| `**/__pycache__/` | regenerated; should never be committed |
| `**/.DS_Store` | macOS metadata |
| `.pytest_cache/` | regenerated |
| `spore_packages/` (empty) | package install dir, gitignored |
| `std/` (top-level: `col`, `crypto`, `data`, `embed`, `ml`, `net`, `quantum`) | confirmed leftover; replaced by `setlhare/stdlib/` (Python) until a `.sl`-implemented stdlib is needed in v0.3+ |

## Moved

| From | To | Reason |
|------|----|--------|
| `vscode/` | `tools/vscode-setlhare/` | editor extensions belong under `tools/` |

## Added (Phase 0)

- `.gitignore` (Python + Node + LLVM + Setlhare build artifacts)
- `LICENSE` (Apache-2.0)
- `.editorconfig`
- `.pre-commit-config.yaml`
- `pyproject.toml` (expanded — ruff, mypy, pytest, coverage config)
- `README.md` (rewritten; honest about pre-alpha status)
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.devcontainer/{devcontainer.json,Dockerfile,postCreate.sh}`
- `.github/workflows/{ci.yml,spec.yml}`
- `.github/CODEOWNERS` (with `@YOUR-GITHUB-USERNAME` placeholder)
- `.github/ISSUE_TEMPLATE/{bug_report.yml,spec_rfc.yml}`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `docs/spec/{00-overview,01-lexical,02-syntax,03-types,04-ownership,05-modules,06-concurrency,07-errors,08-abi,09-stdlib}.md`
- `docs/PHASE0-AUDIT.md` (this file)
- `grammar/tree-sitter-setlhare/{package.json,grammar.js,README.md}`
- `setlhare/compiler/hir.py` (placeholder, v0.2)
- `setlhare/compiler/mir.py` (placeholder, v0.2)
- `tests/conformance/README.md`

## Deferred (intentionally, until after first commit)

- Splitting `setlhare/compiler/bytecode.py` into
  `setlhare/compiler/codegen/bytecode/` + new `setlhare/vm/` — risks
  breaking existing imports; will be a focused PR under the v0.2 milestone.
- Gating `llvm_backend.py` / `wasm_backend.py` behind feature flags — same.
- Writing actual conformance tests — first PR under v0.1.
- Building out the tree-sitter grammar — v0.7 milestone.
- Setting up GitHub Actions secrets, Codecov, release workflow — after
  the repo is on GitHub.

## Outstanding placeholders that MUST be filled before pushing

- [ ] `.github/CODEOWNERS`: replace `@YOUR-GITHUB-USERNAME` with the real handle.
- [ ] `SECURITY.md`: set up `security@setlhare-lang.org` (or replace the address).
- [ ] `README.md`: badges (CI, license, version) — add after first push.
