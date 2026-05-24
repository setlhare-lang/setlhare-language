from __future__ import annotations

import argparse
import pathlib
import sys

from .runtime.interpreter import Interpreter
from .compiler.driver import compile_file
from .tools.spore import Spore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="setlhare", description="Setlhare language toolchain")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run a .sl source file")
    run_p.add_argument("file")

    repl_p = sub.add_parser("repl", help="Start a small Setlhare REPL")

    check_p = sub.add_parser("check", help="Parse and type-check a file using the compiler skeleton")
    check_p.add_argument("file")

    build_p = sub.add_parser("build", help="Compile a file to selected backend artifacts")
    build_p.add_argument("file")
    build_p.add_argument("--target", choices=["bytecode", "llvm", "wasm"], default="bytecode")

    spore_p = sub.add_parser("spore", help="Run the Spore package manager")
    spore_sub = spore_p.add_subparsers(dest="spore_cmd", required=True)
    spore_sub.add_parser("init")
    spore_sub.add_parser("install").add_argument("package")
    spore_sub.add_parser("test")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "run":
            Interpreter().run_file(pathlib.Path(args.file))
            return 0
        if args.cmd == "repl":
            Interpreter().repl()
            return 0
        if args.cmd in {"check", "build"}:
            compile_file(pathlib.Path(args.file), target=getattr(args, "target", "bytecode"), emit=args.cmd == "build")
            return 0
        if args.cmd == "spore":
            spore = Spore(pathlib.Path.cwd())
            if args.spore_cmd == "init":
                spore.init()
            elif args.spore_cmd == "install":
                spore.install(args.package)
            elif args.spore_cmd == "test":
                spore.test()
            return 0
    except Exception as exc:  # noqa: BLE001 - CLI should format all toolchain failures.
        print(f"setlhare: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
