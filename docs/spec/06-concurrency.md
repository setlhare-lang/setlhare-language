# Concurrency

> **Status:** Draft skeleton · v0.2 (`spawn`) · v0.5 (actors fully)

Setlhare's concurrency model is **actor-first, shared-memory-second**.

## 1. Actors

An actor owns its private state. Other code interacts with it only by
sending messages.

```setlhare
actor Counter {
    state count: int = 0

    on inc() {
        self.count = self.count + 1
    }

    on get() -> int {
        return self.count
    }
}
```

Each actor runs on a single logical thread of execution. Multiple actors
may run in parallel. Messages are processed one at a time, in arrival
order.

## 2. Spawning

```setlhare
let counter := spawn Counter { }
counter.inc()           // fire-and-forget
let n := counter.get()? // ask, with response
```

`spawn` produces an `ActorRef<A>`. Dropping the last `ActorRef`
schedules the actor for shutdown.

## 3. `go` blocks

```setlhare
go {
    print("running on a worker")
}
```

A `go` block is a one-shot, anonymous actor. It cannot hold state and
cannot receive messages.

## 4. Channels

(TODO v0.5: define `Sender<T>` / `Receiver<T>` semantics, bounded vs.
unbounded, closing semantics.)

## 5. Memory model

- Within a single actor, execution is strictly sequential.
- Across actors, only **message passing** establishes happens-before.
- Shared memory via `Arc<Mutex<T>>` is permitted but discouraged.

## 6. Cancellation

(TODO v0.5: how cancellation propagates between actors.)
