from babycli._utils import console_ok, console_err, console_warn, redact_secrets


def test_console_ok(capsys):
    console_ok("database connected")
    out = capsys.readouterr().out
    assert "[OK]" in out
    assert "database connected" in out


def test_console_err(capsys):
    console_err("connection refused")
    out = capsys.readouterr().out
    assert "[FAIL]" in out
    assert "connection refused" in out


def test_console_warn(capsys):
    console_warn("slow response")
    out = capsys.readouterr().out
    assert "[WARN]" in out
    assert "slow response" in out


def test_redact_secrets_hides_password():
    result = redact_secrets("POSTGRES_PASSWORD", "hunter2")
    assert result == "***"


def test_redact_secrets_hides_secret_key():
    result = redact_secrets("JWT_SECRET_KEY", "mysecret")
    assert result == "***"


def test_redact_secrets_shows_non_secret():
    result = redact_secrets("POSTGRES_HOST", "localhost")
    assert result == "localhost"
