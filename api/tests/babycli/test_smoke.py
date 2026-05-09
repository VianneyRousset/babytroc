import subprocess

import pytest

SUBCOMMANDS = [
    ["python", "-m", "babycli", "--help"],
    ["python", "-m", "babycli", "check", "--help"],
    ["python", "-m", "babycli", "config", "--help"],
    ["python", "-m", "babycli", "danger-mode", "--help"],
    ["python", "-m", "babycli", "db", "--help"],
    ["python", "-m", "babycli", "db", "seed", "--help"],
    ["python", "-m", "babycli", "lint", "--help"],
    ["python", "-m", "babycli", "logs", "--help"],
    ["python", "-m", "babycli", "server", "--help"],
    ["python", "-m", "babycli", "setup", "--help"],
    ["python", "-m", "babycli", "stats", "--help"],
    ["python", "-m", "babycli", "user", "--help"],
]


@pytest.mark.parametrize("cmd", SUBCOMMANDS, ids=[" ".join(c[3:]) for c in SUBCOMMANDS])
def test_help_exits_zero(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
