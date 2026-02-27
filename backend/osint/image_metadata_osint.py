from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from PIL import ExifTags, Image
except ImportError:  # Pillow is optional until installed
    ExifTags = None
    Image = None


def _convert_gps(value: Any) -> float | None:
    """Convert EXIF GPS rational tuples into decimal coordinates."""
    try:
        degrees = float(value[0][0]) / float(value[0][1])
        minutes = float(value[1][0]) / float(value[1][1])
        seconds = float(value[2][0]) / float(value[2][1])
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    except Exception:
        return None


def _extract_gps(gps_info: dict[str, Any]) -> dict[str, float] | None:
    lat = _convert_gps(gps_info.get("GPSLatitude"))
    lon = _convert_gps(gps_info.get("GPSLongitude"))
    if lat is None or lon is None:
        return None

    if gps_info.get("GPSLatitudeRef") == "S":
        lat = -lat
    if gps_info.get("GPSLongitudeRef") == "W":
        lon = -lon

    return {"latitude": round(lat, 6), "longitude": round(lon, 6)}


def collect_image_metadata(image_path: str) -> dict[str, Any]:
    """
    Extract useful metadata from an image file.

    Return schema:
    {
      "success": bool,
      "file": {...},
      "camera": {...},
      "timestamps": {...},
      "location": {...} | None,
      "raw_exif": {...},
      "error": str | None
    }
    """
    path = Path(image_path)

    if Image is None:
        return {
            "success": False,
            "error": "Pillow is not installed. Run: pip install pillow",
        }

    if not path.exists() or not path.is_file():
        return {"success": False, "error": "Image file not found"}

    try:
        with Image.open(path) as img:
            exif = img.getexif()

            parsed_exif: dict[str, Any] = {}
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id)) if ExifTags else str(tag_id)
                parsed_exif[tag_name] = str(value)

            gps_raw = exif.get_ifd(0x8825) if hasattr(exif, "get_ifd") else None
            gps_named: dict[str, Any] = {}
            if gps_raw and ExifTags:
                for gps_tag, gps_value in gps_raw.items():
                    gps_name = ExifTags.GPSTAGS.get(gps_tag, str(gps_tag))
                    gps_named[gps_name] = gps_value

            location = _extract_gps(gps_named) if gps_named else None

            return {
                "success": True,
                "file": {
                    "name": path.name,
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "size_bytes": path.stat().st_size,
                },
                "camera": {
                    "make": parsed_exif.get("Make"),
                    "model": parsed_exif.get("Model"),
                    "lens_model": parsed_exif.get("LensModel"),
                    "software": parsed_exif.get("Software"),
                },
                "timestamps": {
                    "date_time": parsed_exif.get("DateTime"),
                    "date_time_original": parsed_exif.get("DateTimeOriginal"),
                    "date_time_digitized": parsed_exif.get("DateTimeDigitized"),
                },
                "location": location,
                "raw_exif": parsed_exif,
                "error": None,
            }
    except Exception as exc:
        return {"success": False, "error": f"Failed to read image metadata: {exc}"}
