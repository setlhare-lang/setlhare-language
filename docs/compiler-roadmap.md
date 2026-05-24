# Compiler Roadmap

## v0.1 MVP

- Interpreter with Setlhare-to-Python lowering
- Lexer, parser skeleton, type checker skeleton, borrow checker skeleton
- Bytecode, LLVM, and WASM placeholder emitters
- Spore package manager skeleton

## v0.2 Parser and AST

- Pratt expression parser
- Full block parser
- First-class AST for functions, structs, traits, actors, enums, macros, attributes
- Rich diagnostics with spans and fix suggestions

## v0.3 Type system

- Hindley-Milner style inference with gradual `Dyn`
- Generics, trait constraints, algebraic data types
- Typed `Result<T, E>` and exhaustiveness checking

## v0.4 Safety

- Ownership graph
- Move analysis
- Shared and exclusive borrows
- Lifetime region inference
- Actor isolation checks

## v0.5 Backends

- Register bytecode VM
- LLVM lowering through llvmlite
- WASM MVP target
- Debug info and package builds

## v1.0 Tooling

- Spore registry and lockfiles
- LSP diagnostics/completion/rename
- Canopy IDE or polished VS Code extension
- Formatter, docs generator, test runner
