# Ownership, Borrowing, Lifetimes

> **Status:** Draft skeleton · v0.4 milestone (enforcement)

## 1. The three rules

1. Every value has exactly one **owner**.
2. When the owner goes out of scope, the value is dropped.
3. A value may be **borrowed** (`&T`) any number of times *or* mutably
   borrowed (`&mut T`) exactly once, but never both at once.

## 2. Move semantics

Assignment, function argument passing, and `return` **move** the value
unless the type implements `Copy`.

```setlhare
s1 := "hello"        // s1 owns the string
s2 := s1             // s1 is moved; reading s1 here is a compile error
```

Primitive numeric types, `bool`, `char`, and `&T` are `Copy`. User-defined
types are not unless they derive `Copy` and contain only `Copy` fields.

## 3. Borrowing

```setlhare
func read(name: &str) -> int { ... }      // immutable borrow
func grow(buf: &mut Vec<int>) { ... }     // exclusive borrow
```

Borrows must not outlive the value they reference. The compiler infers
lifetimes for the common cases (elision rules — TODO §4).

## 4. Lifetime elision rules

(TODO v0.4: define elision rules — likely Rust-style 3-rule scheme.)

## 5. Drop order

Values are dropped in **reverse order of declaration** within a scope.
Fields are dropped in **declaration order** within a struct.

## 6. Interior mutability

Interior mutability is opt-in via `Cell<T>` and `RefCell<T>` in the
standard library. These types are **not** `Sync`.

## 7. Send / Sync

A type is `Send` if it can be transferred across actor boundaries.
A type is `Sync` if `&T` can be shared across actors.

(TODO v0.4: auto-trait derivation rules.)
