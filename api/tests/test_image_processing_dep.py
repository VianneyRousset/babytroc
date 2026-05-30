import asyncio

from babytroc.infrastructure.image_processing import (
    get_image_processing_semaphore,
    init_image_processing_dependency,
)


def test_init_and_get_returns_same_semaphore():
    sem = asyncio.Semaphore(3)
    init_image_processing_dependency(sem)
    assert get_image_processing_semaphore() is sem


def test_init_overwrites_previous_semaphore():
    init_image_processing_dependency(asyncio.Semaphore(1))
    new_sem = asyncio.Semaphore(5)
    init_image_processing_dependency(new_sem)
    assert get_image_processing_semaphore() is new_sem


async def test_semaphore_is_usable_as_async_context_manager():
    init_image_processing_dependency(asyncio.Semaphore(2))
    sem = get_image_processing_semaphore()
    async with sem:
        assert sem._value == 1
