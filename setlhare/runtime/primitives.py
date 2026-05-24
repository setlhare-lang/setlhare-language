from __future__ import annotations

from setlhare.stdlib.result import Err, Ok, Result


def __unwrap(value):
    if isinstance(value, Ok):
        return value.value
    if isinstance(value, Err):
        raise RuntimeError(value.error)
    return value


def type_of(value):
    return type(value).__name__


def assert_(condition, message="assertion failed"):
    if not condition:
        raise AssertionError(message)
    return True


def exports():
    return {"__unwrap": __unwrap, "type_of": type_of, "assert": assert_}
