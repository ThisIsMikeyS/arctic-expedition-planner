"""
Unit tests for PDF and JSON export functions in export.py
"""

import unittest
import os
import json
from src.export import export_to_json
from src.planner import Waypoint, Itinerary

class TestExport(unittest.TestCase):
    def setUp(self):
        """Prepare a simple test itinerary."""
        self.waypoints = [
            Waypoint("Camp", 70.0, 20.0, 0.0, 10.0, 100),
            Waypoint("Lake", 70.1, 20.1, 5.0, 12.0, 120)
        ]
        self.itinerary = Itinerary(self.waypoints)
        self.json_file = "test_itinerary_output.json"

    def test_export_to_json(self):
        """Test that JSON export writes expected structure to file."""
        export_to_json(self.itinerary, self.json_file)
        self.assertTrue(os.path.exists(self.json_file))

        with open(self.json_file, "r") as f:
            data = json.load(f)
            self.assertIn("itinerary", data)
            self.assertEqual(len(data["itinerary"]), 2)
            self.assertEqual(data["itinerary"][0]["name"], "Camp")

    def tearDown(self):
        """Remove test output file if it exists."""
        if os.path.exists(self.json_file):
            os.remove(self.json_file)

if __name__ == '__main__':
    unittest.main()