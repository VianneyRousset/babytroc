"""Cross-domain write boundary violation checker."""

import ast
from pathlib import Path

ALLOWED_CROSS_DOMAIN_WRITES: set[tuple[str, str]] = {
    ("auth", "user"),
    ("loan", "item"),
}

WRITE_PREFIXES = (
    "create", "update", "delete", "add", "remove", "send",
    "accept", "reject", "cancel", "upload", "like", "unlike",
    "save", "unsave", "invalidate", "ensure", "insert",
)

READ_PREFIXES = (
    "get", "list", "read", "count", "check",
    "search", "find", "exists",
)


def _get_domains_root() -> Path:
    import babytroc
    return Path(babytroc.__file__).parent / "domains"


def get_domain_name(file_path: Path) -> str | None:
    parts = file_path.parts
    try:
        idx = parts.index("domains")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    except ValueError:
        pass
    return None


def is_handler_file(file_path: Path) -> bool:
    return file_path.name == "handlers.py"


def is_write_function(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(p) for p in WRITE_PREFIXES)


def is_read_function(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(p) for p in READ_PREFIXES)


def extract_imports(
    file_path: Path,
) -> list[tuple[str, list[str], int]]:
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [
                alias.name for alias in node.names
                if alias.name != "*"
            ]
            imports.append((node.module, names, node.lineno))
    return imports


def _get_target_domain(
    module_path: str, source_domain: str,
) -> str | None:
    if not module_path.startswith("babytroc.domains."):
        return None
    parts = module_path.split(".")
    if len(parts) < 4:
        return None
    target_domain = parts[2]
    if target_domain == source_domain:
        return None
    if "models" in parts:
        return None
    if "services" not in parts:
        return None
    if (source_domain, target_domain) in ALLOWED_CROSS_DOMAIN_WRITES:
        return None
    return target_domain


def check_file(
    file_path: Path, *, strict: bool = False,
) -> list[str]:
    source_domain = get_domain_name(file_path)
    if source_domain is None:
        return []
    if is_handler_file(file_path):
        return []

    violations = []
    for module_path, names, lineno in extract_imports(file_path):
        target_domain = _get_target_domain(
            module_path, source_domain,
        )
        if target_domain is None:
            continue
        for name in names:
            if is_write_function(name):
                violations.append(
                    f"{file_path}:{lineno}: "
                    f"cross-domain write import '{name}' "
                    f"from '{module_path}' "
                    f"({source_domain} → {target_domain}). "
                    f"Use events instead."
                )
            elif strict and not is_read_function(name):
                violations.append(
                    f"{file_path}:{lineno}: "
                    f"ambiguous cross-domain import '{name}' "
                    f"from '{module_path}' "
                    f"({source_domain} → {target_domain}). "
                    f"Consider if this should be an event."
                )
    return violations


def check_boundaries(*, strict: bool = False) -> list[str]:
    """Run boundary check, return list of violation strings."""
    domains_root = _get_domains_root()
    if not domains_root.exists():
        return [f"Error: {domains_root} not found."]

    all_violations = []
    for py_file in sorted(domains_root.rglob("*.py")):
        if (
            "services" not in py_file.parts
            and "handlers" not in py_file.name
        ):
            continue
        all_violations.extend(check_file(py_file, strict=strict))
    return all_violations
