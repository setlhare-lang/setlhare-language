# Setlhare Language Guide

## Bindings

```setlhare
name = "mutable by default"
count := 42       // immutable
mut score = 0     // explicit mutable
```

## Functions

```setlhare
func square(n) => n * n

func greet(name) {
    print("Hello ${name}")
}
```

## Control flow

Everything is designed to become expression-oriented. The MVP supports statement lowering:

```setlhare
if score > 10 {
    print("high")
} elif score == 10 {
    print("exact")
} else {
    print("low")
}
```

## Results

```setlhare
value := Ok(42)
print(value?)
```

## Concurrency

```setlhare
func work(n) {
    print("worker ${n}")
}

task := spawn work(1)
task.join()
```

## Future static type syntax

```setlhare
func id<T>(value: T) -> T => value

struct Point {
    x: Float
    y: Float
}

enum Option<T> {
    Some(T)
    None
}
```
