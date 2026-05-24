from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class Result(Generic[T, E]):
    def is_ok(self) -> bool:
        return isinstance(self, Ok)

    def is_err(self) -> bool:
        return isinstance(self, Err)


@dataclass(frozen=True)
class Ok(Result[T, E]):
    value: T

    def map(self, f: Callable[[T], U]) -> Ok[U, E]:
        return Ok(f(self.value))

    def unwrap(self) -> T:
        return self.value


@dataclass(frozen=True)
class Err(Result[T, E]):
    error: E

    def map(self, f: Callable[[T], U]) -> Err[U, E]:
        return Err(self.error)

    def unwrap(self) -> T:
        raise RuntimeError(self.error)
