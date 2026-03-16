from PIL import Image, ExifTags
import logging

logger = logging.getLogger("osint_api")

def _to_decimal(coords, ref):
    """Converts Degrees, Minutes, Seconds to Decimal Degrees."""
    try:
        d = float(coords[0])
        m = float(coords[1])
        s = float(coords[2])
        decimal = d + (m / 60.0) + (s / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return round(decimal, 6)
    except:
        return None

def collect_image_metadata(file_path: str) -> dict:
    try:
        img = Image.open(file_path)
        exif = img._getexif()
        if not exif:
            return {"success": True, "metadata": {}, "location": None}

        readable_exif = {}
        gps_info = {}

        for tag, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for t in value:
                    sub_tag = ExifTags.GPSTAGS.get(t, t)
                    gps_info[sub_tag] = value[t]
            else:
                readable_exif[tag_name] = str(value)

        # Build location data if GPS exists
        location = None
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = _to_decimal(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
            lon = _to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
            if lat and lon:
                location = {
                    "latitude": lat,
                    "longitude": lon,
                    "google_maps": f"https://www.google.com/maps?q={lat},{lon}"
                }

        return {"success": True, "metadata": readable_exif, "location": location}
    except Exception as e:
        logger.error(f"Image Metadata Error: {e}")
        return {"success": False, "error": str(e)}























































