"""Conformance tests for Slice 2: structs, enums, impl blocks, variant patterns."""

from __future__ import annotations

import pytest

from setlhare.errors import SetlhareRuntimeError
from setlhare.runtime.interpreter import Interpreter


def run(src: str) -> Interpreter:
    i = Interpreter()
    i.run_source(src)
    return i


def out(capsys) -> str:
    return capsys.readouterr().out.strip()


# ── struct declaration & literal ──────────────────────────────────────


def test_struct_named_construction(capsys):
    run("struct Point { x, y }\np := Point { x: 3, y: 4 }\nprint(p.x)\nprint(p.y)")
    assert capsys.readouterr().out.splitlines() == ["3", "4"]


def test_struct_field_assignment(capsys):
    run("struct Cell { value }\nmut c = Cell { value: 0 }\nc.value = 42\nprint(c.value)")
    assert out(capsys) == "42"


def test_struct_compound_field_assignment(capsys):
    run("struct Counter { n }\nmut c = Counter { n: 1 }\nc.n += 10\nprint(c.n)")
    assert out(capsys) == "11"


def test_struct_unknown_field_rejected():
    with pytest.raises(SetlhareRuntimeError):
        Interpreter().run_source("struct P { x }\nq := P { y: 1 }")


def test_struct_equality(capsys):
    run("struct V { a, b }\np := V { a: 1, b: 2 }\nq := V { a: 1, b: 2 }\nprint(p == q)")
    assert out(capsys) == "True"


# ── impl methods ──────────────────────────────────────────────────────


def test_impl_method_call(capsys):
    run(
        "struct Point { x, y }\n"
        "impl Point {\n"
        "    func sum() => self.x + self.y\n"
        "}\n"
        "p := Point { x: 5, y: 6 }\n"
        "print(p.sum())"
    )
    assert out(capsys) == "11"


def test_impl_method_with_args(capsys):
    run(
        "struct Vec { x }\n"
        "impl Vec {\n"
        "    func scale(k) => self.x * k\n"
        "}\n"
        "v := Vec { x: 4 }\n"
        "print(v.scale(3))"
    )
    assert out(capsys) == "12"


# ── enums ─────────────────────────────────────────────────────────────


def test_enum_unit_variant(capsys):
    run("enum Color { Red, Green, Blue }\nc := Color::Green\nprint(c)")
    assert out(capsys) == "Color::Green"


def test_enum_payload_variant(capsys):
    run("enum Maybe { Some(v), None }\nm := Maybe::Some(42)\nprint(m)")
    assert out(capsys) == "Maybe::Some(42)"


def test_enum_unknown_variant_rejected():
    with pytest.raises(SetlhareRuntimeError):
        Interpreter().run_source("enum E { A }\nx := E::B")


def test_enum_equality(capsys):
    run("enum E { A, B }\nprint(E::A == E::A)\nprint(E::A == E::B)")
    assert capsys.readouterr().out.splitlines() == ["True", "False"]


# ── variant patterns in match ─────────────────────────────────────────


def test_match_unit_variant(capsys):
    run(
        "enum Light { Red, Green }\n"
        "func describe(l) {\n"
        "    match l {\n"
        '        case Light::Red => return "stop"\n'
        '        case Light::Green => return "go"\n'
        "    }\n"
        "}\n"
        "print(describe(Light::Red))\nprint(describe(Light::Green))"
    )
    assert capsys.readouterr().out.splitlines() == ["stop", "go"]


def test_match_payload_binding(capsys):
    run(
        "enum Maybe { Some(v), None }\n"
        "func unwrap_or(m, default) {\n"
        "    match m {\n"
        "        case Maybe::Some(v) => return v\n"
        "        case Maybe::None => return default\n"
        "    }\n"
        "}\n"
        "print(unwrap_or(Maybe::Some(7), 0))\n"
        "print(unwrap_or(Maybe::None, 99))"
    )
    assert capsys.readouterr().out.splitlines() == ["7", "99"]


def test_match_wildcard_binding(capsys):
    run(
        "enum Pair { Both(a, b), One(x) }\n"
        "func first(p) {\n"
        "    match p {\n"
        "        case Pair::Both(a, _) => return a\n"
        "        case Pair::One(x) => return x\n"
        "    }\n"
        "}\n"
        "print(first(Pair::Both(10, 20)))\n"
        "print(first(Pair::One(5)))"
    )
    assert capsys.readouterr().out.splitlines() == ["10", "5"]


def test_enum_method(capsys):
    run(
        "enum Shape { Circle(r), Square(s) }\n"
        "impl Shape {\n"
        "    func area() {\n"
        "        match self {\n"
        "            case Shape::Circle(r) => return 3 * r * r\n"
        "            case Shape::Square(s) => return s * s\n"
        "        }\n"
        "    }\n"
        "}\n"
        "print(Shape::Circle(2).area())\n"
        "print(Shape::Square(4).area())"
    )
    assert capsys.readouterr().out.splitlines() == ["12", "16"]
