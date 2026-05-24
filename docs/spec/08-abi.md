# ABI & Layout

> **Status:** Draft skeleton · v0.8–0.9 milestones

The Setlhare ABI is **not stable** until v1.0. Anything in this document
may change between minor versions.

## 1. Data layout

By default, structs are laid out with implementation-defined ordering and
padding (the compiler may reorder fields for size).

```setlhare
#[repr(C)]
struct Point { x: f32, y: f32 }
```

The `#[repr(C)]` attribute forces C-compatible layout: field order
preserved, natural alignment, no field reordering.

Other reprs (TODO v0.9):
- `#[repr(transparent)]` — single-field newtype, same layout as inner
- `#[repr(packed)]`      — no padding
- `#[repr(Tag)]` on enums — discriminant size (`u8`, `u16`, `u32`, `u64`)

## 2. Calling convention

- Setlhare-to-Setlhare: implementation-defined (the compiler chooses).
- `extern "C"` functions use the platform C ABI.
- `extern "system"` uses the platform system ABI (Windows: stdcall on x86).

## 3. FFI

```setlhare
extern "C" {
    func sqrt(x: f64) -> f64
}

#[no_mangle]
extern "C" func setlhare_init() { ... }
```

Crossing an FFI boundary requires `unsafe` (TODO: confirm).

## 4. Bytecode format (v0.2)

(TODO: stack-based vs. register-based decision; instruction encoding.)

## 5. WASM target (v0.8)

(TODO: memory model, exports, host bindings.)

## 6. LLVM target (v0.9)

(TODO: how MIR maps to LLVM IR; what optimization passes we rely on.)
