from __future__ import annotations

import argparse
import json
import pathlib
import subprocess


class Spore:
    def __init__(self, root: pathlib.Path):
        self.root = root
        self.manifest = root / "Spore.toml"

    def init(self):
        if self.manifest.exists():
            print("Spore.toml already exists")
            return
        self.manifest.write_text(
            '[package]\nname = "app"\nversion = "0.1.0"\n\n[deps]\n', encoding="utf-8"
        )
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "main.sl").write_text(
            'func main() {\n    print("Hello from Setlhare")\n}\n', encoding="utf-8"
        )
        print("created Setlhare package")

    def install(self, package: str):
        lock = self.root / "Spore.lock.json"
        data = json.loads(lock.read_text()) if lock.exists() else {"deps": []}
        if package not in data["deps"]:
            data["deps"].append(package)
        lock.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"recorded dependency {package!r} (registry integration planned)")

    def test(self):
        tests = sorted((self.root / "tests").glob("*.sl")) if (self.root / "tests").exists() else []
        for test in tests:
            subprocess.run(["python", "-m", "setlhare.cli", "run", str(test)], check=True)
        print(f"ran {len(tests)} tests")


def main(argv=None):
    p = argparse.ArgumentParser(prog="spore")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("install").add_argument("package")
    sub.add_parser("test")
    args = p.parse_args(argv)
    s = Spore(pathlib.Path.cwd())
    if args.cmd == "init":
        s.init()
    elif args.cmd == "install":
        s.install(args.package)
    elif args.cmd == "test":
        s.test()


if __name__ == "__main__":
    main()
