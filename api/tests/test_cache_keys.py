from app.infrastructure.cache_keys import cache_key_hash


class TestCacheKeyHash:
    def test_deterministic(self):
        h1 = cache_key_hash(a=1, b="hello")
        h2 = cache_key_hash(a=1, b="hello")
        assert h1 == h2

    def test_order_independent(self):
        h1 = cache_key_hash(b="hello", a=1)
        h2 = cache_key_hash(a=1, b="hello")
        assert h1 == h2

    def test_none_excluded(self):
        h1 = cache_key_hash(a=1)
        h2 = cache_key_hash(a=1, b=None)
        assert h1 == h2

    def test_different_values_different_hash(self):
        h1 = cache_key_hash(a=1)
        h2 = cache_key_hash(a=2)
        assert h1 != h2

    def test_length(self):
        h = cache_key_hash(a=1)
        assert len(h) == 16
