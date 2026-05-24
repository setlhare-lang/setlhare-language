# Production-readiness status

Setlhare is now structured as a real language implementation instead of a source-to-Python prototype.

## Implemented without shortcuts

- Dedicated lexer with precise line/column diagnostics
- Recursive-descent parser that produces a typed Setlhare AST
- Tree-walking runtime over the AST, not Python source translation
- Lexical environments with mutable and immutable binding enforcement
- First-class Setlhare functions and closures
- Expression parser with precedence for arithmetic, comparison, boolean, calls, fields, indexing, and `?`
- Lists, dictionaries, sets, strings, integers, floats, booleans, and nil
- `if`, `elif`, `else`, `while`, `for`, `match`, `return`, `break`, and `continue`
- String interpolation via Setlhare expression parsing
- `Result`, `Ok`, `Err`, and runtime `?` unwrapping
- Thread-backed `spawn` and `go`
- Import dispatch for standard-library namespaces
- Conservative type-checking pass with symbol tracking
- Early ownership/borrow pass enforcing immutable assignment rules
- CLI smoke-tested for run/check/build
- Pytest runtime coverage

## Not production-complete yet

A production language is not only syntax. It also requires a stable specification, conformance tests, memory model proof, optimizer, package security, release process, ABI policy, fuzzing, and long-term compatibility guarantees.

The current repository is a serious compiler/runtime foundation, but the following are explicitly not complete:

- Full static type system with generics, traits, and sum-type exhaustiveness
- Full Rust-grade borrow checking with moves, references, aliasing regions, and lifetime inference
- Native code generation through LLVM
- WASM binary emission
- Incremental compilation
- Formal language specification
- Production LSP with semantic tokens, refactors, and cross-file indexing
- Secure package registry implementation for Spore

## Engineering path to production

1. Freeze MVP grammar and add golden parser tests.
2. Add AST lowering to HIR and typed MIR.
3. Implement Hindley-Milner-style inference extended with traits and gradual types.
4. Implement region-based ownership checking over MIR.
5. Add bytecode VM with explicit opcodes and snapshot tests.
6. Add LLVM and WASM backends from MIR.
7. Add fuzzing for lexer/parser/runtime.
8. Add standard-library conformance tests.
9. Add package-lock security model and registry signing.
10. Publish compatibility policy and release process.
