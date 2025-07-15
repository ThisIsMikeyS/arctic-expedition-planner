# -*- coding: utf-8 -*-
"""
Unit tests for utility functions in utils.py
"""

import unittest
from src.utils import is_valid_coordinate, haversine_distance, format_coords

class TestUtils(unittest.TestCase):
    def test_is_valid_coordinate(self):
        """Validates proper geographic coordinate ranges."""
        self.assertTrue(is_valid_coordinate(45.0))
        self.assertFalse(is_valid_coordinate(1000.0))
        self.assertTrue(is_valid_coordinate(-89.999))
        self.assertFalse(is_valid_coordinate(-200.0))

    def test_format_coords(self):
        """Test that coordinate formatting returns a correct tuple of floats."""
        self.assertEqual(format_coords("60.0", "25.0"), "60.0000\u00B0, 25.0000\u00B0")

    def test_haversine_distance_zero(self):
        """Distance between same point should be 0."""
        dist = haversine_distance(70.0, 20.0, 70.0, 20.0)
        self.assertEqual(dist, 0.0)

    def test_haversine_distance_value(self):
        """Ensure valid haversine distance is returned between known points."""
        dist = haversine_distance(69.6496, 18.9560, 69.7000, 19.0000)
        self.assertGreater(dist, 1.0)
        self.assertLess(dist, 10.0)

if __name__ == '__main__':
    unittest.main()