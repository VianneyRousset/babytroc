from app.infrastructure.config import S3Config


def test_s3_config_from_env(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://minio:9000")
    monkeypatch.setenv("S3_ACCESS_KEY", "minioadmin")
    monkeypatch.setenv("S3_SECRET_KEY", "minioadmin")
    monkeypatch.setenv("S3_BUCKET", "babytroc-images")
    monkeypatch.setenv("S3_PUBLIC_URL", "https://images.babytroc.ch")

    config = S3Config.from_env()

    assert config.endpoint_url == "http://minio:9000"
    assert config.access_key == "minioadmin"
    assert config.secret_key == "minioadmin"
    assert config.bucket == "babytroc-images"
    assert config.public_url == "https://images.babytroc.ch"
