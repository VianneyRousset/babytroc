import asyncio
from io import BytesIO

import aioboto3

from app.infrastructure.config import S3Config

IMAGE_SIZES = (128, 256, 512, 1024)


def _get_s3_client(config: S3Config):
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=config.endpoint_url,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
    )


def image_key(name: str, size: int) -> str:
    return f"{name}_{size}.webp"


async def upload_image_variants(
    config: S3Config,
    name: str,
    variants: dict[int, BytesIO],
) -> None:
    async with _get_s3_client(config) as client:
        await asyncio.gather(
            *(
                client.put_object(
                    Bucket=config.bucket,
                    Key=image_key(name, size),
                    Body=data.getvalue(),
                    ContentType="image/webp",
                )
                for size, data in variants.items()
            )
        )


async def delete_image_variants(
    config: S3Config,
    name: str,
) -> None:
    async with _get_s3_client(config) as client:
        await client.delete_objects(
            Bucket=config.bucket,
            Delete={
                "Objects": [{"Key": image_key(name, size)} for size in IMAGE_SIZES],
            },
        )
