#!/usr/bin/env python3
"""Check cross-domain write boundary violations.

Rule: domains may import and READ (query) any other domain's models freely,
but WRITES (create/update/delete) to another domain must go through events,
not direct service imports.

Allowed:
  - Any file can import models from any domain (read access)
  - Any file can import read/get/list functions from any domain
  - handlers.py files can import write functions (they are the cross-domain write path)
  - Services within the SAME domain can import anything from that domain

Forbidden:
  - A service in domain X importing a write function from domain Y's services

Usage:
  python scripts/check_domain_boundaries.py [--strict]

  --strict: also flag cross-domain read service imports (not just writes)

Exit codes:
  0: no violations
  1: violations found
"""

import ast
import sys
from pathlib import Path

WRITE_PREFIXES = (
    "create",
    "update",
    "delete",
    "add",
    "remove",
    "send",
    "accept",
    "reject",
    "cancel",
    "upload",
    "like",
    "unlike",
    "save",
    "unsave",
    "invalidate",
    "ensure",
    "insert",
)

READ_PREFIXES = (
    "get",
    "list",
    "read",
    "count",
    "check",
    "search",
    "find",
    "exists",
)

DOMAINS_ROOT = Path("app/domains")


def get_domain_name(file_path: Path) -> str | None:
    """Extract domain name from a file path like app/domains/item/services/create.py."""
    parts = file_path.parts
    try:
        idx = parts.index("domains")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    except ValueError:
        pass
    return None


def is_handler_file(file_path: Path) -> bool:
    """Check if this is a handlers.py file (exempt from write restrictions)."""
    return file_path.name == "handlers.py"


def is_write_function(name: str) -> bool:
    """Determine if a function name looks like a write operation."""
    lower = name.lower()
    return any(lower.startswith(prefix) for prefix in WRITE_PREFIXES)


def is_read_function(name: str) -> bool:
    """Determine if a function name looks like a read operation."""
    lower = name.lower()
    return any(lower.startswith(prefix) for prefix in READ_PREFIXES)


def extract_imports(file_path: Path) -> list[tuple[str, list[str], int]]:
    """Extract all imports from a Python file.

    Returns list of (module_path, imported_names, line_number).
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [alias.name for alias in node.names if alias.name != "*"]
            imports.append((node.module, names, node.lineno))
    return imports


def check_file(file_path: Path, strict: bool = False) -> list[str]:
    """Check a single file for domain boundary violations.

    Returns list of violation messages.
    """
    source_domain = get_domain_name(file_path)
    if source_domain is None:
        return []

    # handlers.py is exempt — it's the official cross-domain write path
    if is_handler_file(file_path):
        return []

    violations = []

    for module_path, names, lineno in extract_imports(file_path):
        # Only check imports from app.domains.*.services
        if not module_path.startswith("app.domains."):
            continue

        parts = module_path.split(".")
        # app.domains.{target_domain}.services...
        if len(parts) < 4:
            continue

        target_domain = parts[2]

        # Same domain — always allowed
        if target_domain == source_domain:
            continue

        # Model imports are always allowed (read access)
        if "models" in parts:
            continue

        # Check if importing from services
        if "services" not in parts:
            continue

        # Check each imported name
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


def main():
    strict = "--strict" in sys.argv

    if not DOMAINS_ROOT.exists():
        print(f"Error: {DOMAINS_ROOT} not found. Run from project root.")
        sys.exit(2)

    all_violations = []

    for py_file in sorted(DOMAINS_ROOT.rglob("*.py")):
        # Only check service files and handler files
        if "services" not in py_file.parts and "handlers" not in py_file.name:
            continue
        violations = check_file(py_file, strict=strict)
        all_violations.extend(violations)

    if all_violations:
        print(f"Found {len(all_violations)} domain boundary violation(s):\n")
        for v in all_violations:
            print(f"  {v}")
        print()
        print("Fix: move cross-domain write calls to event handlers (app/domains/*/handlers.py)")
        sys.exit(1)
    else:
        print("No domain boundary violations found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
