import asyncio

_image_processing_semaphore: asyncio.Semaphore


def init_image_processing_dependency(semaphore: asyncio.Semaphore) -> None:
    global _image_processing_semaphore
    _image_processing_semaphore = semaphore


def get_image_processing_semaphore() -> asyncio.Semaphore:
    return _image_processing_semaphore
