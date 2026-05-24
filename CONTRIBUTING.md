# Contributing to Setlhare

Thank you for your interest. This document explains how to propose changes,
which changes are expected to be controversial, and how the project is run
while it is pre-alpha.

## Before you write code

1. **Read the spec.** `docs/spec/` is the source of truth for syntax and
   semantics. If your change affects observable language behavior, it must
   be reflected in the spec first.
2. **Read the milestones.** We do not accept v0.5 features in v0.1. See
   `README.md` and the GitHub milestones page.
3. **Open an RFC issue** for any of the following:
   - New keyword, operator, or syntactic form
   - Change to the type system, ownership rules, or memory model
   - New stdlib module
   - New compiler IR or pass
   - Anything that would break existing examples

## Local development

```bash
git clone https://github.com/setlhare-lang/setlhare.git
cd setlhare
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

pytest -q                          # full test suite
ruff check . && ruff format .      # lint + format
mypy setlhare                      # type check
```

Or use the dev container (recommended): "Reopen in Container" in VS Code,
or open a GitHub Codespace.

## Branching & PRs

- `main` is protected. All changes go through pull requests.
- One logical change per PR. Refactors and feature work do not mix.
- Every PR must include:
  - **Tests.** New behavior needs new tests; bug fixes need regression tests.
  - **Spec impact.** If language behavior changes, link the affected
    `docs/spec/...` file (and update it in the same PR).
  - **Conformance.** If you are adding a language feature, add at least
    one test under `tests/conformance/`.
- CI must be green before review.

## Commit messages

Use Conventional Commits:

```
type(scope): short summary

Longer body if needed. Reference issues with #123.

Spec: docs/spec/03-types.md (if applicable)
```

Types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`,
`chore`, `spec`.

Scopes: `lexer`, `parser`, `typecheck`, `borrow`, `mir`, `codegen`,
`vm`, `runtime`, `stdlib`, `spore`, `lsp`, `grammar`, `docs`.

## Coding standards

- Python ≥ 3.11. We use modern syntax (`match`, PEP 604 unions).
- Type hints required in new code in `setlhare/compiler/` and
  `setlhare/parser/`. Other areas are tightened over time.
- No silent `except Exception`. Use `setlhare.errors` types.
- No `print` debugging in committed code — use the logging module.

## Architecture decisions

Significant architectural choices are captured as ADRs in `docs/adr/`.
If you propose one, open an issue first to discuss before submitting an ADR PR.

## Releases

- We do not ship release zips. Use git tags (`v0.1.0a1`, ...).
- A release is cut when the milestone for that version is closed.

## Code of Conduct

Participation in this project is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities privately.
