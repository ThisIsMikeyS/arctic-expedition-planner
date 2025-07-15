"""
test_planner.py

Unit tests for the core logic in planner.py, covering:

- Waypoint: attribute handling, negative altitudes, zero-speed cases
- Itinerary: total distance, estimated time, and dictionary export

Focuses on validating expedition data models and calculations.
"""

import unittest
from src.planner import Waypoint, Itinerary

class TestWaypoint(unittest.TestCase):
    def test_create_waypoint(self):
        """Ensure Waypoint initializes all attributes correctly."""
        wp = Waypoint("Base", 69.65, 18.95, 0.0, 10.0, 35)
        self.assertEqual(wp.name, "Base")
        self.assertEqual(wp.latitude, 69.65)
        self.assertEqual(wp.longitude, 18.95)
        self.assertEqual(wp.distance_km, 0.0)
        self.assertEqual(wp.estimated_speed_kph, 10.0)
        self.assertEqual(wp.altitude_m, 35)

    def test_negative_altitude(self):
        """Allow negative altitudes (e.g., Dead Sea or below sea level travel)."""
        wp = Waypoint("Below Sea", 30.0, 31.5, 10.0, 5.0, -50)
        self.assertEqual(wp.altitude_m, -50)

    def test_zero_speed(self):
        """Ensure zero speed doesn't cause division errors in Itinerary."""
        wp = Waypoint("Still Point", 70.0, 20.0, 5.0, 0.0, 100)
        itinerary = Itinerary([wp])
        self.assertEqual(itinerary.estimated_time(), 0.0)


class TestItinerary(unittest.TestCase):
    def setUp(self):
        """Create test itinerary with various edge conditions."""
        self.waypoints = [
            Waypoint("A", 70.0, 20.0, 0.0, 10.0, 50),
            Waypoint("B", 70.1, 20.1, 0.0, 0.0, 60),  # zero speed leg
            Waypoint("C", 70.2, 20.2, 5.0, 15.0, 70)
        ]
        self.itinerary = Itinerary(self.waypoints)

    def test_total_distance(self):
        """Sum of all waypoint distances."""
        self.assertEqual(self.itinerary.total_distance(), 5.0)

    def test_estimated_time_mixed_speeds(self):
        """
        Should skip zero-speed leg to avoid division by zero.
        Only C's leg contributes: 5.0 / 15.0 = 0.333...
        """
        expected_time = 5.0 / 15.0
        self.assertAlmostEqual(self.itinerary.estimated_time(), expected_time, places=4)

    def test_to_dict_output(self):
        """Ensure correct structure is produced for export."""
        data = self.itinerary.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn("itinerary", data)
        self.assertEqual(len(data["itinerary"]), 3)
        self.assertIn("name", data["itinerary"][0])
        self.assertEqual(data["itinerary"][2]["altitude_m"], 70)


if __name__ == "__main__":
    unittest.main()
