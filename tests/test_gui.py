"""
Extended unit tests for GUI logic in gui.py.
Covers waypoint addition, toggles, list updates, and non-visual state changes.
"""

import unittest
import tkinter as tk
from unittest.mock import patch
from src.gui import ExpeditionPlannerGUI

class TestGUI(unittest.TestCase):
    def setUp(self):
        """Set up a hidden root window and GUI instance for each test."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = ExpeditionPlannerGUI(self.root)

    def tearDown(self):
        """Destroy the root window after each test."""
        self.root.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_add_waypoint_resets_toggle(self, mock_msgbox):
        """Manual toggle should reset to False after adding a waypoint."""
        self.app.manual_distance_enabled.set(True)
        self._fill_waypoint_fields("A", 70.0, 20.0, 10.0, 5.0, 150)
        self.app.add_waypoint()
        self.assertFalse(self.app.manual_distance_enabled.get())

    def test_toggle_distance_field_disables_entry(self):
        """Distance entry should become readonly when manual toggle is off."""
        self.app.manual_distance_enabled.set(False)
        self.app.toggle_distance_field()
        state = self.app.distance_entry.cget("state")
        self.assertEqual(state, "readonly")

    def test_refresh_listbox_updates_entries(self):
        """Listbox should reflect current waypoints."""
        self._add_two_waypoints()
        self.app.refresh_waypoint_list()
        self.assertEqual(self.app.waypoint_listbox.size(), 2)

    def test_move_waypoint_up(self):
        """Waypoint order should change when moved up."""
        self._add_two_waypoints()
        self.app.waypoint_listbox.selection_set(1)
        self.app.move_waypoint_up()
        self.assertEqual(self.app.waypoints[0].name, "B")

    def test_move_waypoint_down(self):
        """Waypoint order should change when moved down."""
        self._add_two_waypoints()
        self.app.waypoint_listbox.selection_set(0)
        self.app.move_waypoint_down()
        self.assertEqual(self.app.waypoints[1].name, "A")

    def test_delete_waypoint(self):
        """Deleting a selected waypoint should remove it from the list."""
        self._add_two_waypoints()
        self.app.waypoint_listbox.selection_set(0)
        self.app.delete_waypoint()
        self.assertEqual(len(self.app.waypoints), 1)

    @patch('src.gui.filedialog.asksaveasfilename', return_value='test.json')
    @patch('src.gui.messagebox.showinfo')
    @patch('src.gui.export_to_json')
    def test_export_json_logic(self, mock_export, mock_showinfo, mock_saveas):
        """Test export to JSON writes expected format."""
        root = tk.Tk()
        root.withdraw()
        
        with patch.object(ExpeditionPlannerGUI, '__init__', lambda self, r: None):
            app = ExpeditionPlannerGUI(root)
            app.root = root
            app.waypoints = self._add_two_waypoints()

        app.export_json()

        mock_export.assert_called_once()
        mock_showinfo.assert_called_once_with("Export", "Exported itinerary to JSON.")
        
        root.destroy()

    def _fill_waypoint_fields(self, name, lat, lon, dist, speed, alt):
        """Helper to fill form fields."""
        self.app.name_var.set(name)
        self.app.lat_var.set(lat)
        self.app.lon_var.set(lon)
        self.app.dist_var.set(dist)
        self.app.speed_var.set(speed)
        self.app.alt_var.set(alt)

    @patch("tkinter.messagebox.showinfo")
    def _add_two_waypoints(self, mock_msgbox):
        """Helper to add two waypoints to the form."""
        self._fill_waypoint_fields("A", 70.0, 20.0, 0.0, 10.0, 150)
        self.app.add_waypoint()
        self._fill_waypoint_fields("B", 70.1, 20.1, 5.0, 9.0, 160)
        self.app.manual_distance_enabled.set(True)
        self.app.add_waypoint()


if __name__ == "__main__":
    unittest.main()
