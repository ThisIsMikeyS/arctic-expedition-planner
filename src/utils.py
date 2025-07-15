# -*- coding: utf-8 -*-
"""
Utility functions for the Arctic Expedition Planner.
Includes common validation, formatting, or helper methods.
"""

from math import radians, sin, cos, sqrt, atan2

def format_coords(lat, lon):
    """Format lat/lon as a degree string for display, converting input to float if needed."""
    lat = float(lat)
    lon = float(lon)
    return f"{lat:.4f}°, {lon:.4f}°"

def is_valid_coordinate(value: float) -> bool:
    """Check if a float value is a valid lat/lon coordinate."""
    return -90.0 <= value <= 90.0 or -180.0 <= value <= 180.0

def km_to_miles(km: float) -> float:
    """Convert kilometers to miles."""
    return round(km * 0.621371, 2)

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth
    using the Haversine formula. Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)
