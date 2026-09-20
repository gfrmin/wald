"""The kernel may import the standard-library modules below and itself. Nothing else: not the charter, not the oracle,
not the environment. If you need another module, ask in QUESTIONS.md; the author edits this list."""
import ast, pathlib, sys
ALLOW = {"wald", "__future__", "fractions", "dataclasses", "typing", "enum", "itertools", "functools", "collections", "abc", "operator", "numbers", "math", "ast", "hashlib", "json", "keyword", "pathlib"}
BANNED_CALLS = {"eval", "exec", "compile", "__import__", "open", "input", "breakpoint", "globals", "locals", "vars"}
bad = []
for path in sorted(pathlib.Path(sys.argv[1]).rglob("*.py")):
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        mods = []
        if isinstance(node, ast.Import): mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom): mods = [node.module or "wald"] if node.level == 0 else ["wald"]
        for m in mods:
            if m.split(".")[0] not in ALLOW: bad.append(f"{path}:{node.lineno}: import of {m}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            bad.append(f"{path}:{node.lineno}: call to {node.func.id}()")
print("\n".join(bad) if bad else "imports ok"); sys.exit(1 if bad else 0)
