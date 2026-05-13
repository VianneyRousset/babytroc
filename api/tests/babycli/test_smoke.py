import subprocess

import pytest

SUBCOMMANDS = [
    ["babycli", "--help"],
    ["babycli", "check", "--help"],
    ["babycli", "config", "--help"],
    ["babycli", "danger-mode", "--help"],
    ["babycli", "db", "--help"],
    ["babycli", "db", "seed", "--help"],
    ["babycli", "lint", "--help"],
    ["babycli", "logs", "--help"],
    ["babycli", "server", "--help"],
    ["babycli", "setup", "--help"],
    ["babycli", "stats", "--help"],
    ["babycli", "user", "--help"],
]


@pytest.mark.parametrize("cmd", SUBCOMMANDS, ids=[" ".join(c[3:]) for c in SUBCOMMANDS])
def test_help_exits_zero(cmd):
    result = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
