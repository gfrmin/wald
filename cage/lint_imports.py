"""The kernel may import the standard-library modules below and itself. Nothing else: not the charter, not the oracle,
not the environment. If you need another module, ask in QUESTIONS.md; the author edits this list.

Bans added 2026-10-01, each with the witness that forced it (cage/lint_poisons/, each of which this lint must refuse):
- `pathlib` only in src/wald/datafile.py, the one file the kernel reads (KERNEL.md). Witness proc_environ:
  `pathlib.Path("/proc/self/environ").read_bytes()` in law.py passed this lint and printed KIT_SEED from the kit.
- `__builtins__`, `__loader__`, `__spec__`, `__dict__`, as a name or an attribute. Witness builtins_open:
  `getattr(__builtins__, "open")` reaches the banned open() without calling it by its bare name.
- `/proc` in any string. Witness proc_literal: the process's own environment is a file under /proc.
The lint is the second line. The first is the kit's: the seed is read and spent before the kernel is imported
(wald-charter laws/kit_seed.py, kit v0.14), so none of it is left in the process to find."""
import ast, pathlib, sys
ALLOW = {"wald", "__future__", "fractions", "dataclasses", "typing", "enum", "itertools", "functools", "collections", "abc", "operator", "numbers", "math", "ast", "hashlib", "json", "keyword", "pathlib"}
ONLY_IN = {"pathlib": "datafile.py"}
BANNED_CALLS = {"eval", "exec", "compile", "__import__", "open", "input", "breakpoint", "globals", "locals", "vars"}
BANNED_NAMES = {"__builtins__", "__loader__", "__spec__", "__dict__"}
def names_proc(v): return "/proc" in v if isinstance(v, str) else isinstance(v, bytes) and b"/proc" in v
root = pathlib.Path(sys.argv[1]); bad = []
for path in sorted(root.rglob("*.py")):
    rel = path.relative_to(root).as_posix()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        mods = []
        if isinstance(node, ast.Import): mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom): mods = [node.module or "wald"] if node.level == 0 else ["wald"]
        for m in mods:
            top = m.split(".")[0]
            if top not in ALLOW: bad.append(f"{path}:{node.lineno}: import of {m}")
            elif top in ONLY_IN and rel != ONLY_IN[top]: bad.append(f"{path}:{node.lineno}: import of {m} outside src/wald/{ONLY_IN[top]}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            bad.append(f"{path}:{node.lineno}: call to {node.func.id}()")
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES: bad.append(f"{path}:{node.lineno}: use of {node.id}")
        if isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES: bad.append(f"{path}:{node.lineno}: use of .{node.attr}")
        if isinstance(node, ast.Constant) and names_proc(node.value): bad.append(f"{path}:{node.lineno}: a string naming /proc")
print("\n".join(bad) if bad else "imports ok"); sys.exit(1 if bad else 0)
