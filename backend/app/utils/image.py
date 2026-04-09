import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags

from app.config import settings


def generate_filename(extension: str) -> str:
    return f"{uuid.uuid4().hex}.{extension}"


def get_upload_path(filename: str) -> Path:
    now = datetime.now()
    dir_path = Path(settings.UPLOAD_DIR) / "originals" / str(now.year) / f"{now.month:02d}"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / filename


def get_thumbnail_path(filename: str, size: int) -> Path:
    now = datetime.now()
    stem = Path(filename).stem
    dir_path = Path(settings.UPLOAD_DIR) / "thumbnails" / str(now.year) / f"{now.month:02d}"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / f"{stem}_{size}.webp"


def create_thumbnail(source_path: Path, size: int) -> Path:
    thumb_path = get_thumbnail_path(source_path.name, size)
    with Image.open(source_path) as img:
        img.thumbnail((size, size))
        img.save(thumb_path, "WEBP", quality=80)
    return thumb_path


def extract_exif(file_path: Path) -> dict | None:
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None
            readable = {}
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                try:
                    json.dumps(value)
                    readable[tag_name] = value
                except (TypeError, ValueError):
                    readable[tag_name] = str(value)
            return readable
    except Exception:
        return None


def get_image_dimensions(file_path: Path) -> tuple[int, int]:
    with Image.open(file_path) as img:
        return img.size
