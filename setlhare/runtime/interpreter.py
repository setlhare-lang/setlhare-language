from __future__ import annotations

import builtins
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any

from setlhare.errors import ImmutableAssignmentError, SetlhareRuntimeError
from setlhare.parser import ast as A
from setlhare.parser.parser import Parser


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


@dataclass(slots=True)
class BindingInfo:
    value: Any
    mutable: bool = True
    type_name: str | None = None


@dataclass(slots=True)
class Environment:
    parent: Environment | None = None
    values: dict[str, BindingInfo] = field(default_factory=dict)

    def define(
        self, name: str, value: Any, mutable: bool = True, type_name: str | None = None
    ) -> None:
        if name in self.values and not self.values[name].mutable:
            raise ImmutableAssignmentError(f"cannot redefine immutable binding '{name}'")
        self.values[name] = BindingInfo(value, mutable, type_name)

    def assign(self, name: str, value: Any) -> None:
        env = self._find(name)
        if env is None:
            self.define(name, value, mutable=True)
            return
        binding = env.values[name]
        if not binding.mutable:
            raise ImmutableAssignmentError(f"cannot assign to immutable binding '{name}'")
        binding.value = value

    def get(self, name: str) -> Any:
        env = self._find(name)
        if env is None:
            raise SetlhareRuntimeError(f"undefined name '{name}'")
        return env.values[name].value

    def _find(self, name: str) -> Environment | None:
        if name in self.values:
            return self
        return self.parent._find(name) if self.parent else None


class SetlhareFunction:
    def __init__(
        self,
        node: A.Function,
        closure: Environment,
        interpreter: Interpreter,
        receiver: Any = None,
        is_method: bool = False,
    ):
        self.node = node
        self.closure = closure
        self.interpreter = interpreter
        self.__name__ = node.name
        self.receiver = receiver
        self.is_method = is_method

    def bind(self, receiver: Any) -> SetlhareFunction:
        return SetlhareFunction(self.node, self.closure, self.interpreter, receiver, is_method=True)

    def __call__(self, *args: Any) -> Any:
        params = self.node.params
        if self.is_method:
            args = (self.receiver, *args)
        if len(args) != len(params):
            raise SetlhareRuntimeError(
                f"function '{self.node.name}' expected {len(params)} arguments, got {len(args)}"
            )
        env = Environment(self.closure)
        for name, value in zip(params, args, strict=True):
            env.define(name, value, mutable=True)
        try:
            return self.interpreter._execute_block(self.node.body or A.Block(), env)
        except ReturnSignal as ret:
            return ret.value

    def __repr__(self) -> str:
        return f"<func {self.node.name}>"


class StructType:
    """Runtime representation of a Setlhare struct."""

    def __init__(self, name: str, fields: list[str]):
        self.name = name
        self.fields = fields
        self.methods: dict[str, SetlhareFunction] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> StructInstance:
        if args and kwargs:
            raise SetlhareRuntimeError(
                f"struct '{self.name}': mix of positional and named args not allowed"
            )
        if args:
            if len(args) != len(self.fields):
                raise SetlhareRuntimeError(
                    f"struct '{self.name}' expected {len(self.fields)} fields, got {len(args)}"
                )
            data = dict(zip(self.fields, args, strict=True))
        else:
            for k in kwargs:
                if k not in self.fields:
                    raise SetlhareRuntimeError(f"struct '{self.name}' has no field '{k}'")
            data = {f: kwargs.get(f) for f in self.fields}
        return StructInstance(self, data)

    def __repr__(self) -> str:
        return f"<struct {self.name}>"


class StructInstance:
    __slots__ = ("_data", "_type")

    def __init__(self, type_: StructType, data: dict[str, Any]):
        object.__setattr__(self, "_type", type_)
        object.__setattr__(self, "_data", data)

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        if name in data:
            return data[name]
        type_ = object.__getattribute__(self, "_type")
        if name in type_.methods:
            return type_.methods[name].bind(self)
        raise AttributeError(f"struct '{type_.name}' has no field or method '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        data = object.__getattribute__(self, "_data")
        type_ = object.__getattribute__(self, "_type")
        if name not in data:
            raise SetlhareRuntimeError(f"struct '{type_.name}' has no field '{name}'")
        data[name] = value

    def __repr__(self) -> str:
        type_ = object.__getattribute__(self, "_type")
        data = object.__getattribute__(self, "_data")
        body = ", ".join(f"{k}: {v!r}" for k, v in data.items())
        return f"{type_.name} {{ {body} }}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StructInstance):
            return NotImplemented
        return object.__getattribute__(self, "_type") is object.__getattribute__(
            other, "_type"
        ) and object.__getattribute__(self, "_data") == object.__getattribute__(other, "_data")

    def __hash__(self) -> int:
        return id(self)


class EnumType:
    """Runtime representation of a Setlhare enum (sum type)."""

    def __init__(self, name: str, variants: dict[str, list[str]]):
        self.name = name
        self.variants = variants  # variant_name -> field names
        self.methods: dict[str, SetlhareFunction] = {}

    def get_variant(self, variant: str) -> Any:
        if variant not in self.variants:
            raise SetlhareRuntimeError(f"enum '{self.name}' has no variant '{variant}'")
        fields = self.variants[variant]
        if not fields:
            return EnumValue(self, variant, ())
        return _VariantConstructor(self, variant, fields)

    def __repr__(self) -> str:
        return f"<enum {self.name}>"


class _VariantConstructor:
    def __init__(self, enum_type: EnumType, variant: str, fields: list[str]):
        self.enum_type = enum_type
        self.variant = variant
        self.fields = fields

    def __call__(self, *args: Any) -> EnumValue:
        if len(args) != len(self.fields):
            raise SetlhareRuntimeError(
                f"variant '{self.enum_type.name}::{self.variant}' expected "
                f"{len(self.fields)} args, got {len(args)}"
            )
        return EnumValue(self.enum_type, self.variant, tuple(args))

    def __repr__(self) -> str:
        return f"<variant {self.enum_type.name}::{self.variant}>"


class EnumValue:
    __slots__ = ("_type", "payload", "variant")

    def __init__(self, type_: EnumType, variant: str, payload: tuple):
        self._type = type_
        self.variant = variant
        self.payload = payload

    def __getattr__(self, name: str) -> Any:
        type_ = object.__getattribute__(self, "_type")
        if name in type_.methods:
            return type_.methods[name].bind(self)
        raise AttributeError(
            f"enum value '{type_.name}::{object.__getattribute__(self, 'variant')}' "
            f"has no method '{name}'"
        )

    def __repr__(self) -> str:
        if not self.payload:
            return f"{self._type.name}::{self.variant}"
        body = ", ".join(repr(p) for p in self.payload)
        return f"{self._type.name}::{self.variant}({body})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnumValue):
            return NotImplemented
        return (
            self._type is other._type
            and self.variant == other.variant
            and self.payload == other.payload
        )

    def __hash__(self) -> int:
        return hash((id(self._type), self.variant, self.payload))


class BoundMethod:
    def __init__(self, receiver: Any, name: str):
        self.receiver = receiver
        self.name = name

    def __call__(self, *args: Any) -> Any:
        r = self.receiver
        if self.name == "map":
            return (
                type(r)([args[0](x) for x in r])
                if isinstance(r, list)
                else getattr(r, self.name)(*args)
            )
        if self.name == "filter":
            return (
                type(r)([x for x in r if args[0](x)])
                if isinstance(r, list)
                else getattr(r, self.name)(*args)
            )
        if self.name == "sum" and isinstance(r, (list, tuple, set)):
            return builtins.sum(r)
        if self.name == "parallel":
            from setlhare.stdlib.collections import parallel

            workers = args[0] if args else 4
            return parallel(r, workers)
        attr = getattr(r, self.name)
        return attr(*args)


class Interpreter:
    """Tree-walking Setlhare runtime.

    This is no longer a source-to-Python shortcut. Files are lexed, parsed into a Setlhare
    AST, semantically checked at runtime, and evaluated by this VM-style interpreter.
    """

    def __init__(self) -> None:
        self.parser = Parser()
        self.globals = Environment()
        self._install_builtins()

    def run_file(self, path: pathlib.Path) -> Any:
        source = path.read_text(encoding="utf-8")
        module = self.parser.parse(source, str(path))
        self._execute_module(module, self.globals)
        main = self.globals._find("main")
        if main:
            return self.globals.get("main")()
        return None

    def run_source(self, source: str, filename: str = "<memory>") -> Any:
        module = self.parser.parse(source, filename)
        return self._execute_module(module, self.globals)

    def repl(self) -> None:
        print("Setlhare REPL. Type :quit to exit.")
        while True:
            try:
                line = input("sl> ")
            except EOFError:
                break
            if line.strip() in {":quit", ":q"}:
                break
            try:
                result = self.run_source(line)
                if result is not None:
                    print(result)
            except Exception as exc:
                print(f"error: {exc}")

    def _install_builtins(self) -> None:
        from setlhare.runtime import primitives
        from setlhare.stdlib import (
            actors,
            collections,
            fs,
            http,
            io,
            json,
            math,
            result,
            text,
            time,
        )

        builtins_env: dict[str, Any] = {
            "true": True,
            "false": False,
            "nil": None,
            "print": builtins.print,
            "input": builtins.input,
            "len": len,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "Ok": result.Ok,
            "Err": result.Err,
            "Result": result.Result,
            "spawn": actors.spawn,
            "go": actors.go,
            "Actor": actors.Actor,
            "List": collections.List,
            "parallel": collections.parallel,
            "sleep": time.sleep,
            "io": io,
            "math": math,
            "fs": fs,
            "time": time,
            "json": json,
            "text": text,
            "http": http,
            "actors": actors,
            "col": collections,
            **primitives.exports(),
        }
        for name, value in builtins_env.items():
            self.globals.define(name, value, mutable=False)

    def _execute_module(self, module: A.Module, env: Environment) -> Any:
        result = None
        for stmt in module.body:
            result = self._execute(stmt, env)
        return result

    def _execute_block(self, block: A.Block, env: Environment) -> Any:
        result = None
        for stmt in block.statements:
            result = self._execute(stmt, env)
        return result

    def _execute(self, stmt: Any, env: Environment) -> Any:
        if isinstance(stmt, A.Import):
            return self._import(stmt, env)
        if isinstance(stmt, A.Function):
            env.define(stmt.name, SetlhareFunction(stmt, env, self), mutable=False)
            return None
        if isinstance(stmt, A.StructDecl):
            env.define(stmt.name, StructType(stmt.name, stmt.fields), mutable=False)
            return None
        if isinstance(stmt, A.EnumDecl):
            variants = {v.name: v.fields for v in stmt.variants}
            env.define(stmt.name, EnumType(stmt.name, variants), mutable=False)
            return None
        if isinstance(stmt, A.ImplBlock):
            target = env.get(stmt.target)
            if not isinstance(target, (StructType, EnumType)):
                raise SetlhareRuntimeError(f"impl target '{stmt.target}' is not a struct or enum")
            for method in stmt.methods:
                # Methods take 'self' implicitly: prepend it as first param.
                node = A.Function(
                    method.line,
                    method.col,
                    method.name,
                    ["self", *method.params],
                    method.body,
                    method.return_type,
                )
                target.methods[method.name] = SetlhareFunction(node, env, self)
            return None
        if isinstance(stmt, A.Binding):
            env.define(stmt.name, self._eval(stmt.value, env), stmt.mutable, stmt.type_name)
            return None
        if isinstance(stmt, A.Assign):
            new_value = self._eval(stmt.value, env)
            if stmt.op != "=":
                current = env.get(stmt.name)
                new_value = self._apply_binary(stmt.op[:-1], current, new_value)
            env.assign(stmt.name, new_value)
            return None
        if isinstance(stmt, A.IndexAssign):
            obj = self._eval(stmt.target.obj, env)
            idx = self._eval(stmt.target.index, env)
            new_value = self._eval(stmt.value, env)
            if stmt.op != "=":
                new_value = self._apply_binary(stmt.op[:-1], obj[idx], new_value)
            obj[idx] = new_value
            return None
        if isinstance(stmt, A.AttrAssign):
            obj = self._eval(stmt.target.obj, env)
            name = stmt.target.name
            new_value = self._eval(stmt.value, env)
            if stmt.op != "=":
                new_value = self._apply_binary(stmt.op[:-1], getattr(obj, name), new_value)
            setattr(obj, name, new_value)
            return None
        if isinstance(stmt, A.ExprStmt):
            return self._eval(stmt.expr, env)
        if isinstance(stmt, A.Return):
            raise ReturnSignal(None if stmt.value is None else self._eval(stmt.value, env))
        if isinstance(stmt, A.Break):
            raise BreakSignal()
        if isinstance(stmt, A.Continue):
            raise ContinueSignal()
        if isinstance(stmt, A.If):
            if self._truthy(self._eval(stmt.condition, env)):
                return self._execute_block(stmt.then_block or A.Block(), Environment(env))
            for cond, block in stmt.elifs:
                if self._truthy(self._eval(cond, env)):
                    return self._execute_block(block, Environment(env))
            if stmt.else_block:
                return self._execute_block(stmt.else_block, Environment(env))
            return None
        if isinstance(stmt, A.While):
            result = None
            while self._truthy(self._eval(stmt.condition, env)):
                try:
                    result = self._execute_block(stmt.body or A.Block(), Environment(env))
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return result
        if isinstance(stmt, A.For):
            result = None
            for item in self._eval(stmt.iterable, env):
                loop_env = Environment(env)
                loop_env.define(stmt.name, item, mutable=True)
                try:
                    result = self._execute_block(stmt.body or A.Block(), loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return result
        if isinstance(stmt, A.Match):
            return self._execute_match(stmt, env)
        raise SetlhareRuntimeError(f"unsupported statement {type(stmt).__name__}")

    def _execute_match(self, stmt: A.Match, env: Environment) -> Any:
        value = self._eval(stmt.value, env)
        for case in stmt.cases:
            case_env = Environment(env)
            if not self._pattern_matches(case, value, case_env):
                continue
            return self._execute_block(case.body or A.Block(), case_env)
        return None

    def _pattern_matches(self, case: A.MatchCase, value: Any, env: Environment) -> bool:
        if case.is_wildcard:
            return True
        pattern = case.pattern
        if isinstance(pattern, A.VariantPattern):
            if not isinstance(value, EnumValue):
                return False
            if value._type.name != pattern.type_name or value.variant != pattern.variant:
                return False
            if len(pattern.bindings) != len(value.payload):
                return False
            for binding, payload in zip(pattern.bindings, value.payload, strict=True):
                if binding is not None:
                    env.define(binding, payload, mutable=True)
            return True
        if isinstance(pattern, A.Path):
            # zero-arg variant pattern via path expression
            evaluated = self._eval(pattern, env)
            return evaluated == value
        return self._eval(pattern, env) == value

    def _import(self, stmt: A.Import, env: Environment) -> None:
        path = stmt.module
        table = {
            "std::io": "io",
            "std::math": "math",
            "std::fs": "fs",
            "std::time": "time",
            "std::json": "json",
            "std::text": "text",
            "std::result": "result",
            "col::collections": "collections",
            "net::http": "http",
            "std::actors": "actors",
            "ml::core": "ml",
            "embed::core": "embed",
            "quantum::core": "quantum",
        }
        mod_name = table.get(path, path.split("::")[-1])
        if env._find(mod_name) is not None:
            return None
        try:
            module = __import__(f"setlhare.stdlib.{mod_name}", fromlist=[mod_name])
        except Exception as exc:
            raise SetlhareRuntimeError(f"cannot import module '{path}'") from exc
        env.define(mod_name, module, mutable=False)

    def _eval(self, expr: Any, env: Environment) -> Any:
        if isinstance(expr, A.Literal):
            if isinstance(expr.value, str):
                return self._interpolate(expr.value, env)
            return expr.value
        if isinstance(expr, A.Name):
            return env.get(expr.name)
        if isinstance(expr, A.ListExpr):
            from setlhare.stdlib.collections import List

            return List([self._eval(x, env) for x in expr.items])
        if isinstance(expr, A.SetExpr):
            return {self._eval(x, env) for x in expr.items}
        if isinstance(expr, A.DictExpr):
            return {self._eval(k, env): self._eval(v, env) for k, v in expr.items}
        if isinstance(expr, A.Unary):
            right = self._eval(expr.right, env)
            if expr.op == "-":
                return -right
            if expr.op in {"!", "not"}:
                return not self._truthy(right)
            raise SetlhareRuntimeError(f"unknown unary operator {expr.op}")
        if isinstance(expr, A.Binary):
            if expr.op == "or":
                left = self._eval(expr.left, env)
                return left if self._truthy(left) else self._eval(expr.right, env)
            if expr.op == "and":
                left = self._eval(expr.left, env)
                return self._eval(expr.right, env) if self._truthy(left) else left
            left = self._eval(expr.left, env)
            right = self._eval(expr.right, env)
            return self._apply_binary(expr.op, left, right)
        if isinstance(expr, A.Call):
            fn = self._eval(expr.callee, env)
            args = [self._eval(a, env) for a in expr.args]
            if not callable(fn):
                raise SetlhareRuntimeError(f"value {fn!r} is not callable")
            return fn(*args)
        if isinstance(expr, A.GetAttr):
            obj = self._eval(expr.obj, env)
            if isinstance(obj, (list, tuple, set)) and expr.name in {
                "map",
                "filter",
                "sum",
                "parallel",
            }:
                return BoundMethod(obj, expr.name)
            try:
                return getattr(obj, expr.name)
            except AttributeError as exc:
                raise SetlhareRuntimeError(
                    f"object {obj!r} has no attribute '{expr.name}'"
                ) from exc
        if isinstance(expr, A.StructLit):
            target = env.get(expr.type_name)
            if not isinstance(target, StructType):
                raise SetlhareRuntimeError(f"'{expr.type_name}' is not a struct")
            kwargs = {name: self._eval(value, env) for name, value in expr.fields}
            return target(**kwargs)
        if isinstance(expr, A.Path):
            return self._resolve_path(expr.parts, env)
        if isinstance(expr, A.Index):
            return self._eval(expr.obj, env)[self._eval(expr.index, env)]
        if isinstance(expr, A.ResultUnwrap):
            return self._unwrap(self._eval(expr.expr, env))
        if isinstance(expr, A.Spawn):
            call = expr.call
            if call is None or not isinstance(call, A.Call):
                raise SetlhareRuntimeError(f"{expr.kind} expects a function call")
            fn = self._eval(call.callee, env)
            args = [self._eval(a, env) for a in call.args]
            spawner = env.get(expr.kind)
            return spawner(fn, *args)
        raise SetlhareRuntimeError(f"unsupported expression {type(expr).__name__}")

    def _resolve_path(self, parts: list[str], env: Environment) -> Any:
        if len(parts) < 2:
            return env.get(parts[0])
        head = env.get(parts[0])
        if isinstance(head, EnumType) and len(parts) == 2:
            return head.get_variant(parts[1])
        # Generic attribute walk for module paths.
        value: Any = head
        for part in parts[1:]:
            value = value.get_variant(part) if isinstance(value, EnumType) else getattr(value, part)
        return value

    def _apply_binary(self, op: str, left: Any, right: Any) -> Any:
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "%":
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        raise SetlhareRuntimeError(f"unknown binary operator {op}")

    def _unwrap(self, value: Any) -> Any:
        from setlhare.stdlib.result import Err, Ok

        if isinstance(value, Ok):
            return value.value
        if isinstance(value, Err):
            raise SetlhareRuntimeError(f"unwrapped Err: {value.error}")
        return value

    def _interpolate(self, template: str, env: Environment) -> str:
        def repl(match: re.Match[str]) -> str:
            source = match.group(1)
            parsed = self.parser.parse(source)
            if len(parsed.body) != 1 or not isinstance(parsed.body[0], A.ExprStmt):
                raise SetlhareRuntimeError("interpolation expects a single expression")
            return str(self._eval(parsed.body[0].expr, env))

        return re.sub(r"\$\{([^}]*)\}", repl, template)

    def _truthy(self, value: Any) -> bool:
        return bool(value)
