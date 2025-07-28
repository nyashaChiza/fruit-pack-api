from math import radians, sin, cos, sqrt, atan2
from typing import Dict

def distance_between(start: Dict[str, float], end: Dict[str, float]) -> float:
    """
    Calculate the great-circle distance between two points using the Haversine formula.

    Args:
        start (dict): A dict with 'lat' and 'lng' keys (latitude and longitude in decimal degrees).
        end (dict): Same as start.

    Returns:
        float: Distance in kilometers, rounded to 2 decimal places.

    Raises:
        ValueError: If any of the coordinates are missing or invalid.
    """
    try:
        lat1, lon1 = float(start['lat']), float(start['lng'])
        lat2, lon2 = float(end['lat']), float(end['lng'])
    except (KeyError, TypeError, ValueError):
        raise ValueError("Both `start` and `end` must contain valid 'lat' and 'lng' float values.")

    R_km = 6371.0  # Earth's radius in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R_km * c, 2)
