# Type System

> **Status:** Draft skeleton · v0.3 milestone (enforcement)

## 1. Primitive types

| Type    | Bits / Range | Notes |
|---------|--------------|-------|
| `bool`  | 1            | `true` / `false` |
| `i8` `i16` `i32` `i64` `i128` | signed two's complement | |
| `u8` `u16` `u32` `u64` `u128` | unsigned       | |
| `isize` `usize` | pointer-sized | |
| `f32` `f64` | IEEE 754       | |
| `char`  | 32-bit Unicode scalar | |
| `str`   | UTF-8 string, immutable | |
| `unit`  | `()`         | the singleton type |
| `never` | `!`          | the empty type (no values) |

## 2. Compound types

```
(T1, T2, ...)        // tuple
[T]                  // slice
[T; N]               // fixed-size array
&T  &mut T           // borrow (see ownership.md)
?T                   // shorthand for Option<T>
fn(T1, T2) -> R      // function pointer
```

## 3. Patterns

```ebnf
Pattern  = "_"                              (* wildcard *)
         | Literal
         | Ident [ "@" Pattern ]            (* bind *)
         | Path "(" Pattern { "," Pattern } ")"   (* enum *)
         | Path "{" { Field } [ ".." ] "}"        (* struct *)
         | "(" Pattern { "," Pattern } ")"        (* tuple *)
         | "[" Pattern { "," Pattern } "]"        (* slice *)
         | Pattern "|" Pattern              (* or-pattern *)
         | Expr ".." Expr | Expr "..=" Expr (* range *) ;
```

## 4. Inference

- `name := expr` infers `name`'s type from `expr` and makes it immutable.
- `let mut name = expr` infers and is mutable.
- `let name: T = expr` requires `expr : T`.
- Inference is **local** (Hindley–Milner style within a function body).
  Cross-function inference is **not** performed — function signatures must
  be fully annotated.

## 5. Generics

```setlhare
func max<T: Ord>(a: T, b: T) -> T {
    if a > b { a } else { b }
}
```

Bounds use `:`. Multiple bounds with `+`. Where-clauses (TODO):

```setlhare
func merge<K, V>(a: Map<K, V>, b: Map<K, V>) -> Map<K, V>
    where K: Hash + Eq {
    ...
}
```

## 6. Traits

```setlhare
trait Display {
    func fmt(self) -> str
}

impl Display for int {
    func fmt(self) -> str => int_to_str(self)
}
```

Traits are dispatched statically by default. Dynamic dispatch is opt-in
via `dyn Trait` (TODO: confirm syntax).

## 7. Coercions

There are **no** implicit numeric conversions. Use `as`:

```setlhare
let n: i64 = 42 as i64
```

The only implicit coercion is `&mut T -> &T` (mutability erasure).

(TODO v0.3: deref coercion rules, subtyping for lifetimes.)
