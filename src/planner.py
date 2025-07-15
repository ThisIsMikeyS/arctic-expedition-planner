"""
Data models for the Arctic Expedition Planner.
Defines Waypoint and Itinerary classes with travel estimation logic.
"""

from dataclasses import dataclass

@dataclass
class Waypoint:
    """Represents a point in the expedition route."""
    name: str
    latitude: float
    longitude: float
    distance_km: float
    estimated_speed_kph: float
    altitude_m: int

    def estimated_time_hours(self) -> float:
        """Calculate and return the estimated travel time in hours."""
        if self.estimated_speed_kph > 0:
            return round(self.distance_km / self.estimated_speed_kph, 2)
        return 0.0

@dataclass
class Itinerary:
    """Represents a collection of waypoints and computes overall stats."""
    def __init__(self, waypoints):
        self.waypoints = waypoints

    def total_distance(self):
        """Return total distance of the itinerary."""
        return sum(wp.distance_km for wp in self.waypoints)

    def estimated_time(self):
        """Calculate estimated time in hours based on each waypoint's distance and speed."""
        total_time = 0.0
        for wp in self.waypoints:
            if wp.estimated_speed_kph > 0:
                total_time += wp.distance_km / wp.estimated_speed_kph
        return total_time

    def to_dict(self):
        """Convert itinerary to a serializable dictionary format."""
        return {
            "itinerary": [
                {
                    "name": wp.name,
                    "latitude": wp.latitude,
                    "longitude": wp.longitude,
                    "distance_km": wp.distance_km,
                    "estimated_speed_kph": wp.estimated_speed_kph,
                    "altitude_m": wp.altitude_m
                }
                for wp in self.waypoints
            ]
        }   

