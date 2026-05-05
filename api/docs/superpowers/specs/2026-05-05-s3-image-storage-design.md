# S3 Image Storage Migration

Replace imgpush with S3 (MinIO) + nginx reverse proxy for image storage and serving.

## Context

The API currently uses imgpush — a self-hosted image upload/resize service — as the image backend. Images are uploaded via HTTP POST, retrieved via HTTP GET with optional `?w=` resize parameter, and proxied through the API as raw bytes. This adds latency, couples the API to imgpush's response format, and requires the API to handle image serving traffic.

## Requirements

- Replace imgpush with direct S3 (MinIO) uploads from the API
- On upload, generate 3 webp variants: 256px, 512px, 1024px (max dimension)
- Nginx reverse-proxies the S3 bucket to serve images publicly
- The API does not proxy image bytes — clients build image URLs directly
- Minimal security image processing: validate format, strip EXIF, recompress as webp
- No docker compose

## Architecture

```
Upload:   Client → API → process image → 3 webp variants → MinIO bucket
Read:     Client → nginx → MinIO bucket (API not involved)
```

The API's image read endpoint is removed. Clients construct image URLs using the pattern:

```
{S3_PUBLIC_URL}/{name}_{size}.webp
```

Where `S3_PUBLIC_URL` is the nginx base URL (e.g. `https://images.babytroc.ch`), `name` is the UUID stored in `item_image.name`, and `size` is one of `256`, `512`, `1024`.

## Config

Replace `ImgpushConfig` with `S3Config`:

```python
class S3Config(NamedTuple):
    endpoint_url: str    # S3_ENDPOINT_URL — MinIO internal URL (e.g. http://minio:9000)
    access_key: str      # S3_ACCESS_KEY
    secret_key: str      # S3_SECRET_KEY
    bucket: str          # S3_BUCKET
    public_url: str      # S3_PUBLIC_URL — nginx URL clients use (e.g. https://images.babytroc.ch)
```

Env vars: `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET`, `S3_PUBLIC_URL`.

## Upload Flow

1. Receive image file via existing upload endpoint
2. Validate: confirm file is a valid image (PIL open + verify), reject non-image files
3. Strip all EXIF/metadata (already done via `clear_exif`)
4. Apply EXIF orientation (already done via `apply_exif_orientation`)
5. For each target size (256, 512, 1024):
   - Resize image so max dimension = target size (preserve aspect ratio, only downscale)
   - Encode as webp (quality 80)
   - Upload to S3 as `{uuid}_{size}.webp` with `Content-Type: image/webp`
6. Store UUID in `item_image.name` (same as today)
7. Return image metadata (name, public URL)

## Image URL Resolution

Clients resolve image URLs themselves. The API exposes `S3_PUBLIC_URL` via a config endpoint or includes it in responses where image names appear. The frontend constructs:

```
GET {S3_PUBLIC_URL}/{name}_256.webp   # thumbnail
GET {S3_PUBLIC_URL}/{name}_512.webp   # medium
GET {S3_PUBLIC_URL}/{name}_1024.webp  # full
```

## Nginx Configuration (reference, not managed by API)

```nginx
server {
    listen 80;
    server_name images.babytroc.ch;

    location / {
        proxy_pass http://minio:9000/babytroc-images/;
        proxy_set_header Host minio:9000;
        proxy_hide_header x-amz-request-id;
        proxy_hide_header x-amz-id-2;

        # Cache at nginx level
        proxy_cache_valid 200 30d;
        add_header Cache-Control "public, max-age=2592000, immutable";
    }
}
```

## S3 Client

New module `app/clients/storage/s3.py` using `aioboto3`:

- `upload_image(s3_config, name, size, data)` — PUT object to `{name}_{size}.webp`
- `upload_image_variants(s3_config, name, variants)` — upload all 3 sizes concurrently via `asyncio.gather`
- `delete_image(s3_config, name)` — delete all 3 variants for a given name

## Security Processing

Minimal, focused on preventing malicious uploads:

1. **Format validation** — `PIL.Image.open(fp)` + `image.verify()` rejects non-images and malformed files
2. **EXIF stripping** — removes GPS, camera info, embedded thumbnails (existing `clear_exif`)
3. **Orientation normalization** — applies EXIF orientation then strips (existing `apply_exif_orientation`)
4. **Recompression as webp** — re-encoding destroys any steganographic or polyglot payloads embedded in the original format
5. **Size limit** — max dimension 1024px (existing `limit_image_size`, updated from `MAX_DIMENSION`)

No new dependencies for security — Pillow handles all of this.

## File Changes

### Delete
- `app/clients/networking/imgpush/` — entire directory
- `app/schemas/networking/imgpush.py` — imgpush response schema

### New
- `app/clients/storage/s3.py` — async S3 upload/delete via aioboto3

### Modify
- `app/config.py` — replace `ImgpushConfig` with `S3Config`, update `Config` tuple
- `app/services/image/create.py` — generate 3 webp variants, upload to S3
- `app/services/image/read.py` — remove `get_image_data`, keep DB-only functions
- `app/routers/v1/images/read.py` — remove image proxy endpoint (or return URL)
- `app/clients/networking/__init__.py` — remove imgpush import
- `app/services/image/constants.py` — update `MAX_DIMENSION` to 1024, add `IMAGE_SIZES`
- `CLAUDE.md` — update env var documentation

### Dependencies
- Add `aioboto3` to `pyproject.toml`
- `Pillow` already present (used by `app/utils/image.py`)

## Testing

- Unit test S3 client with mocked aioboto3 session
- Unit test image variant generation (3 sizes, webp format, correct dimensions)
- Integration test upload endpoint produces 3 objects in S3
- Existing chat/item tests that reference images: update fixtures if they depend on imgpush

## Migration

Existing images in imgpush need to be migrated to S3. This is a one-time operation outside the API scope — a script that reads all `item_image` names from the DB, fetches from imgpush, processes to 3 webp sizes, and uploads to MinIO. Not part of this implementation plan.
