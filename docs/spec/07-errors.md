# Errors

> **Status:** Draft skeleton · v0.1 milestone

## 1. The contract

Setlhare has **no exceptions**. Fallible functions return `Result<T, E>`
or `Option<T>`. There is no implicit unwinding.

A `panic` is a bug, not a control-flow tool. It terminates the *actor*
that raised it. Panics outside of actors terminate the program.

## 2. `Result` and `Option`

```setlhare
enum Result<T, E> { Ok(T), Err(E) }
enum Option<T>    { Some(T), None }
```

These types are in the prelude.

## 3. The `?` operator

`expr?` desugars to:

```setlhare
match expr {
    Ok(v)  => v,
    Err(e) => return Err(e.into()),
}
```

For `Option`, `None` propagates analogously. `?` may only be used in
functions whose return type is the same kind (`Result` or `Option`).

## 4. Error trait

```setlhare
trait Error: Display {
    func source(self) -> ?&dyn Error => None
}
```

Any type implementing `Error` can be the `E` of a `Result`.

## 5. `From` for error conversion

```setlhare
trait From<T> {
    func from(value: T) -> Self
}
```

`?` uses `E1: From<E0>` to convert error types up the call stack.

## 6. Panics

```setlhare
panic("invariant violated: count was {n}")
```

A panic prints a message, dumps an actor-local backtrace, and terminates
the current actor. Other actors continue.

(TODO: `catch_panic` for supervisor patterns — v0.5.)
