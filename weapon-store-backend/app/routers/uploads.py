import io
import re
import uuid
import warnings
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.dependencies.auth import get_current_admin_user
from app.models.user import User

router = APIRouter(tags=["Catalog images"])
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
IMAGE_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}


def store_product_image(data: bytes) -> str:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                if image.format not in IMAGE_FORMATS:
                    raise ValueError("Unsupported format")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image dimensions are too large")
                extension, _ = IMAGE_FORMATS[image.format]
                image.verify()
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail="Выберите корректное изображение PNG, JPEG или WebP до 20 мегапикселей",
        ) from exc

    filename = f"{uuid.uuid4().hex}.{extension}"
    directory = Path(settings.PRODUCT_UPLOAD_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_bytes(data)
    return f"/api/media/products/{filename}"


@router.post("/products/images", status_code=201)
async def upload_product_image(
    file: UploadFile,
    current_admin: User = Depends(get_current_admin_user),
):
    try:
        data = await file.read(MAX_IMAGE_BYTES + 1)
    finally:
        await file.close()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Размер изображения не должен превышать 8 МБ")
    image_url = await run_in_threadpool(store_product_image, data)
    return {"image_url": image_url}


@router.get("/media/products/{filename}", include_in_schema=False)
def get_product_image(filename: str):
    if not re.fullmatch(r"[0-9a-f]{32}\.(png|jpg|webp)", filename):
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    path = Path(settings.PRODUCT_UPLOAD_DIR) / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    media_type = next(
        mime for extension, mime in IMAGE_FORMATS.values() if extension == path.suffix.lstrip(".")
    )
    return FileResponse(
        path,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=604800, immutable",
            "X-Content-Type-Options": "nosniff",
        },
    )
