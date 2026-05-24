# Modules & Visibility

> **Status:** Draft skeleton · v0.1 (basic) · v0.6 (full)

## 1. Module = file

Every `.sl` file is a module. The module name is the file's stem (no
`.sl` extension), unless `module Name { ... }` is used.

## 2. Package = directory + manifest

A package is a directory containing `Spore.toml` and a `src/` tree of
modules. The default crate root is `src/main.sl` for binaries and
`src/lib.sl` for libraries.

## 3. Imports

```setlhare
import std::io                    // import a module
import std::io::{print, eprint}   // import items
import math as m                  // alias
import std::collections::*        // glob (discouraged outside prelude)
```

## 4. Visibility

- Items are **private** by default (visible only within the module).
- `pub` makes an item visible to the parent module.
- `pub(crate)` makes it visible within the package.
- `pub(super)` makes it visible to the parent module only.

## 5. Paths

```
Path = ( "self" | "super" | "crate" | Ident ) { "::" Ident }
```

`std::` is implicitly available — the prelude items are imported into
every module.

## 6. The prelude

(TODO v0.1: enumerate prelude items — likely `print`, `Result`, `Option`,
`Vec`, `String`, basic numeric traits.)
