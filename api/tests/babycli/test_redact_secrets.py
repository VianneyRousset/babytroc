from babycli._utils import redact_secrets


class TestRedactSecrets:
    def test_redacts_when_key_matches_secret_pattern(self):
        assert redact_secrets("POSTGRES_PASSWORD", "abc") == "***"
        assert redact_secrets("JWT_SECRET_KEY", "abc") == "***"
        assert redact_secrets("API_TOKEN", "abc") == "***"

    def test_returns_plain_value_for_non_secret_key(self):
        assert redact_secrets("HOST_NAME", "babytroc.ch") == "babytroc.ch"

    def test_masks_userinfo_in_url_value(self):
        assert (
            redact_secrets("REDIS_URL", "redis://:supersecret@h.example.com:6379/0")
            == "redis://***@h.example.com:6379/0"
        )

    def test_masks_user_and_password_userinfo(self):
        assert (
            redact_secrets("REDIS_URL", "redis://alice:s3cret@host:6379/0")
            == "redis://***@host:6379/0"
        )

    def test_url_without_userinfo_unchanged(self):
        assert (
            redact_secrets("S3_PUBLIC_URL", "http://s3.example.com/bucket")
            == "http://s3.example.com/bucket"
        )

    def test_unix_url_with_userinfo_masked(self):
        # The hostname is None for unix:// URLs, so we should still mask cleanly.
        masked = redact_secrets("REDIS_URL", "unix://:pw@/tmp/r.sock?db=0")
        assert "pw" not in masked
        assert "***@" in masked

    def test_unix_url_without_userinfo_unchanged(self):
        value = "unix:///tmp/r.sock?db=0"
        assert redact_secrets("REDIS_URL", value) == value

    def test_non_url_value_unchanged(self):
        assert redact_secrets("DELAY", "0.5") == "0.5"
