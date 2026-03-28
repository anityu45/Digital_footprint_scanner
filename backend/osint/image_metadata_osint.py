from PIL import Image, ExifTags
import logging

logger = logging.getLogger("osint_api")

def _to_decimal(coords, ref):
    """
    Converts Degrees, Minutes, Seconds to Decimal Degrees.
    Safely handles both modern Pillow IFDRational objects and older tuple formats.
    """
    try:
        def safe_float(val):
            # Pillow sometimes returns an IFDRational object, sometimes a (num, den) tuple, 
            # and sometimes just a float/int depending on the image and library version.
            if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                return float(val)
            if isinstance(val, tuple) and len(val) == 2:
                return float(val[0]) / float(val[1])
            return float(val)

        d = safe_float(coords[0])
        m = safe_float(coords[1])
        s = safe_float(coords[2])
        
        decimal = d + (m / 60.0) + (s / 3600.0)
        
        # Invert for South and West
        if ref in ['S', 'W']:
            decimal = -decimal
            
        return round(decimal, 6)
    except Exception as e:
        logger.debug(f"Coordinate conversion failed: {e}")
        return None

def collect_image_metadata(file_path: str) -> dict:
    try:
        # Using a context manager ensures the file is properly closed after reading
        with Image.open(file_path) as img:
            # getexif() is the modern, safe replacement for the private _getexif() method
            exif = img.getexif()
            
            if not exif:
                return {"success": True, "metadata": {}, "location": None}

            readable_exif = {}
            gps_info = {}

            # 1. Extract Standard EXIF Data
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                
                # Prevent massive binary blobs (like MakerNote) from crashing your JSON output
                if isinstance(value, bytes):
                    readable_exif[tag_name] = "<binary data omitted>"
                else:
                    readable_exif[tag_name] = str(value)

            # 2. Extract GPS Data (Modern Pillow Approach)
            # GPS data is stored in a specific Image File Directory (IFD)
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            if gps_ifd:
                for tag_id, value in gps_ifd.items():
                    tag_name = ExifTags.GPSTAGS.get(tag_id, tag_id)
                    gps_info[tag_name] = value

            # 3. Build Location Data
            location = None
            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                lat = _to_decimal(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
                lon = _to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
                
                if lat is not None and lon is not None:
                    location = {
                        "latitude": lat,
                        "longitude": lon,
                        # Fixed the Google Maps formatting to actually work
                        "google_maps": f"https://www.google.com/maps?q={lat},{lon}"
                    }

            return {"success": True, "metadata": readable_exif, "location": location}
            
    except FileNotFoundError:
        logger.error(f"Image not found at path: {file_path}")
        return {"success": False, "error": "File not found"}
    except Exception as e:
        logger.error(f"Image Metadata Error: {e}")
        return {"success": False, "error": str(e)}