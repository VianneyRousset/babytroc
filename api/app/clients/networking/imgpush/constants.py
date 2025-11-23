import aiohttp

TIMEOUT = aiohttp.ClientTimeout(
    connect=1,
    total=5,
)
