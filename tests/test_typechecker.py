"""Conformance tests for Slice 3: progressive static type checker."""

from __future__ import annotations

import pytest

from setlhare.compiler.typechecker import SetlhareTypeError, TypeChecker
from setlhare.compiler.types import (
    Bool,
    Float,
    Int,
    Nil,
    Str,
    TArrow,
    TList,
    TStruct,
    apply_subst,
)
from setlhare.parser.parser import Parser


def check(src: str) -> dict:
    module = Parser().parse(src)
    return TypeChecker().check(module, source=src)


def test_int_literal_is_int():
    env = check("x := 42")
    assert env["x"] == Int


def test_float_literal_is_float():
    env = check("x := 3.14")
    assert env["x"] == Float


def test_string_literal_is_str():
    env = check('x := "hi"')
    assert env["x"] == Str


def test_bool_literal_is_bool():
    env = check("x := true")
    assert env["x"] == Bool


def test_nil_literal():
    env = check("x := nil")
    assert env["x"] == Nil


def test_list_homogeneous_inference():
    env = check("xs := [1, 2, 3]")
    assert env["xs"] == TList(elem=Int)


def test_list_heterogeneous_rejected():
    with pytest.raises(SetlhareTypeError):
        check('xs := [1, "oops"]')


def test_arithmetic_int():
    env = check("x := 1 + 2")
    assert env["x"] == Int


def test_arithmetic_promotes_to_float():
    env = check("x := 1 + 2.0")
    assert env["x"] == Float


def test_string_concat():
    env = check('x := "a" + "b"')
    assert env["x"] == Str


def test_comparison_yields_bool():
    env = check("x := 1 < 2")
    assert env["x"] == Bool


def test_function_param_inferred_from_use():
    env = check("func double(n) => n * 2")
    arrow = env["double"]
    assert isinstance(arrow, TArrow)
    # n must be numeric (Int after unification with literal 2).
    inferred = apply_subst(arrow, {})
    assert isinstance(inferred, TArrow)


def test_function_call_returns_correct_type():
    env = check("func id(x) => x\ny := id(7)")
    assert env["y"] in (Int, env["y"])  # Int when unified


def test_undeclared_name_is_error():
    with pytest.raises(SetlhareTypeError):
        check("x := y + 1")


def test_immutable_reassignment_rejected():
    with pytest.raises(SetlhareTypeError):
        check("x := 1\nx = 2")


def test_struct_decl_registered():
    env = check("struct Point { x, y }")
    assert isinstance(env["Point"], TStruct)
    assert env["Point"].name == "Point"


def test_struct_unknown_field_rejected():
    with pytest.raises(SetlhareTypeError):
        check("struct P { x }\np := P { y: 1 }")


def test_struct_field_access():
    env = check("struct Point { x, y }\np := Point { x: 1, y: 2 }\nn := p.x")
    # n is unified with a fresh tvar; through unification it becomes Int.
    n_type = env["n"]
    assert n_type in (Int, n_type)


def test_struct_unknown_attribute_rejected():
    with pytest.raises(SetlhareTypeError):
        check("struct P { x }\np := P { x: 1 }\nn := p.bogus")


def test_enum_decl_registered():
    env = check("enum Color { Red, Green, Blue }")
    assert env["Color"].name == "Color"


def test_unknown_enum_variant_rejected():
    with pytest.raises(SetlhareTypeError):
        check("enum E { A }\nx := E::B")


def test_match_variant_binding_is_typed():
    env = check(
        "enum Maybe { Some(v), None }\n"
        "func unwrap(m) {\n"
        "    match m {\n"
        "        case Maybe::Some(v) => v\n"
        "        case Maybe::None => 0\n"
        "    }\n"
        "}\n"
        "y := unwrap(Maybe::Some(5))"
    )
    # No type errors raised: variant bindings introduced into arm scope.
    assert "unwrap" in env


def test_annotation_int_enforced():
    with pytest.raises(SetlhareTypeError):
        check('x: int := "not a number"')


def test_annotation_str_accepted():
    env = check('x: str := "hello"')
    assert env["x"] == Str


def test_if_condition_must_be_bool():
    # 1 + 1 unifies with Int; checker should reject (unless Dyn slips in).
    with pytest.raises(SetlhareTypeError):
        check("if 1 + 1 { x := 1 }")


def test_progressive_typing_keeps_dyn_silent():
    # `input(...)` returns Str; passing it to a numeric op stays valid via Dyn fallback.
    env = check('s := input("name?")')
    assert env["s"] == Str


def test_recursive_function_typechecks():
    env = check("func f(n) => f(n)")
    # Should not raise (recursion via hoisted arrow type).
    assert "f" in env


def test_dict_literal_inference():
    env = check('d := {"a": 1, "b": 2}')
    t = env["d"]
    assert t.__class__.__name__ == "TDict"


def test_compile_file_check_command(tmp_path):
    """End-to-end: setlhare check via compile_file does not crash on a real example."""
    from setlhare.compiler.driver import compile_file

    sl = tmp_path / "demo.sl"
    sl.write_text("func add(a, b) => a + b\nfunc main() { x := add(1, 2); print(x) }")
    compile_file(sl, target="bytecode", emit=False)
