# Setlhare Language Specification — Overview

> **Status:** Draft · Pre-alpha · Subject to change without notice until v1.0

This document is the source of truth for the Setlhare language.
Implementations must conform to it. When the implementation and the spec
disagree, the spec wins — unless explicitly amended by an accepted RFC.

## Design goals

1. **Readable.** Source should read like a written sentence in Setswana
   storytelling — subject, verb, object.
2. **Safe.** No null, no uninitialized memory, no data races. Ownership is
   tracked statically.
3. **Predictable.** No surprising implicit conversions, no hidden control flow.
4. **Honest errors.** All fallible operations return `Result<T, E>` or
   `Option<T>`. Crashes are bugs, not features.
5. **Concurrent.** Actors are first-class. Shared mutable state is opt-in
   and explicit.
6. **Embeddable.** The runtime is portable; the compiler produces bytecode,
   WASM, and native code via LLVM.

## Non-goals

- A general-purpose object-oriented language with classes and inheritance.
- Implicit pointers, manual memory management, or unrestricted mutation.
- A scripting language with dynamic typing pervasively across the codebase.
- Source-compatible interop with any existing language.

## Document map

| File | Topic |
|------|-------|
| `01-lexical.md` | Source text, tokens, comments, literals |
| `02-syntax.md`  | EBNF grammar (the canonical form) |
| `03-types.md`   | Type system, inference, generics, traits |
| `04-ownership.md` | Ownership, borrowing, lifetimes |
| `05-modules.md` | Modules, imports, visibility |
| `06-concurrency.md` | Actors, channels, `spawn`/`go` |
| `07-errors.md`  | `Result`, `Option`, the `?` operator, panics |
| `08-abi.md`     | Calling conventions, layout, FFI |
| `09-stdlib.md`  | Standard library surface area |

## Conventions

- Keywords appear in **`monospace`**.
- Non-terminals in the grammar appear as *`italic-monospace`*.
- "Must", "must not", "should", "may" follow [RFC 2119].

[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
