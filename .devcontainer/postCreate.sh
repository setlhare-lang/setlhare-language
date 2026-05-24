#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Python project (editable, with dev extras)"
pip install --user -e ".[dev]"

echo "==> Installing tree-sitter CLI (Rust)"
cargo install --locked tree-sitter-cli || true

echo "==> Installing pre-commit hooks"
pre-commit install || true

echo "==> Verifying toolchain"
python --version
node --version
cargo --version || true
clang --version | head -n1 || true
llc --version | head -n2 || true
wasm-as --version || true
wasm-validate --version || true

echo "==> Ready. Try: setlhare run examples/hello.sl"
