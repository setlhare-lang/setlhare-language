# Standard Library

> **Status:** Draft skeleton · evolving across all milestones

The standard library is split into:

- **Prelude** — items imported into every module automatically
- **Core** — no allocation, no I/O, freestanding-safe (`std::core::*`)
- **Std** — full standard library, depends on OS facilities

## 1. Prelude (always in scope)

| Item            | Kind   |
|-----------------|--------|
| `print`         | function |
| `Option<T>`     | enum |
| `Result<T, E>`  | enum |
| `Some`, `None`  | enum variants |
| `Ok`, `Err`     | enum variants |
| `Vec<T>`        | struct |
| `String`        | struct |
| `Display`       | trait |
| `Debug`         | trait |
| `Clone`         | trait |
| `Copy`          | trait |
| `Eq`, `PartialEq` | traits |
| `Ord`, `PartialOrd` | traits |
| `Hash`          | trait |
| `Default`       | trait |
| `Iterator`      | trait |

## 2. Module surface (target)

| Module             | Status   | Purpose |
|--------------------|----------|---------|
| `std::io`          | v0.1 ✓   | print, eprint, stdin |
| `std::fs`          | v0.1 ✓   | files, paths |
| `std::math`        | v0.1 ✓   | numeric functions |
| `std::text`        | v0.1 ✓   | string manipulation |
| `std::time`        | v0.1 ✓   | clocks, durations |
| `std::collections` | v0.1 ✓   | Vec, HashMap, HashSet, BTreeMap |
| `std::json`        | v0.1 ✓   | parse / serialize |
| `std::http`        | v0.2     | client + server |
| `std::result`      | v0.1 ✓   | Result helpers |
| `std::actors`      | v0.2     | actor primitives |
| `std::crypto`      | v0.5     | hashing, AEAD |
| `std::ml`          | v0.7     | tensor ops (experimental) |
| `std::quantum`     | research | (do not stabilize before v1.0) |
| `std::embed`       | v0.8     | freestanding / no-alloc subset |

(Items marked ✓ already exist as Python implementations in
`setlhare/stdlib/`. They will be re-validated against the spec as the
type checker comes online.)

## 3. Stability

Once a module reaches v1.0, breaking changes require a major version bump.
Pre-1.0, every minor release may break stdlib APIs — but breakage must
be called out in `CHANGELOG.md`.
