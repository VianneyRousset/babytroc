import json
from pathlib import Path
from unittest.mock import patch

from babycli.danger import (
    DANGER_FILE_NAME,
    is_danger_mode,
    _read_danger_file,
    _write_danger_file,
    _clear_danger_file,
)


def test_no_file_means_not_danger(tmp_path):
    with patch("babycli.danger.DANGER_DIR", tmp_path):
        assert is_danger_mode() is False


def test_enable_creates_file(tmp_path):
    with patch("babycli.danger.DANGER_DIR", tmp_path):
        _write_danger_file(ttl_minutes=5)
        assert (tmp_path / DANGER_FILE_NAME).exists()
        data = json.loads((tmp_path / DANGER_FILE_NAME).read_text())
        assert data["ttl_minutes"] == 5
        assert "enabled_at" in data


def test_enabled_file_means_danger(tmp_path):
    with patch("babycli.danger.DANGER_DIR", tmp_path):
        _write_danger_file(ttl_minutes=5)
        assert is_danger_mode() is True


def test_expired_file_means_not_danger(tmp_path):
    with patch("babycli.danger.DANGER_DIR", tmp_path):
        data = {
            "enabled_at": "2020-01-01T00:00:00",
            "ttl_minutes": 1,
        }
        (tmp_path / DANGER_FILE_NAME).write_text(json.dumps(data))
        assert is_danger_mode() is False
        assert not (tmp_path / DANGER_FILE_NAME).exists()


def test_disable_removes_file(tmp_path):
    with patch("babycli.danger.DANGER_DIR", tmp_path):
        _write_danger_file(ttl_minutes=5)
        _clear_danger_file()
        assert not (tmp_path / DANGER_FILE_NAME).exists()


def test_disable_no_file_no_error(tmp_path):
    with patch("babycli.danger.DANGER_DIR", tmp_path):
        _clear_danger_file()
