# tree-sitter-setlhare

Tree-sitter grammar for the Setlhare programming language.

## Status

Stub — v0.7 milestone target. The grammar currently parses a tiny subset
(imports, `func` declarations, `let`/`:=`, literals). It must eventually
mirror `docs/spec/02-syntax.md` exactly.

## Develop

Requires `tree-sitter-cli` (install via `cargo install tree-sitter-cli`
or `npm install`).

```bash
cd grammar/tree-sitter-setlhare
npm install
npx tree-sitter generate
npx tree-sitter test
npx tree-sitter parse ../../examples/hello.sl
```

## Conformance

The hand-written parser in `setlhare/parser/` and this grammar must agree
on every example in `examples/` and every test in `tests/conformance/`.

CI will (TODO) parse every conformance file with both parsers and diff
the trees.
