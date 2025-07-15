"""
GUI for Arctic Expedition Planner, featuring:
1. Waypoint entry form
2. Options to preview waypoints on map and get coordinates from map
3. Options to export to JSON or PDF
4. Current itinerary wapoint display box
5. Buttons to edit the current itinerary
6. Total distance and time summaries
"""

import tkinter as tk
from tkinter import messagebox, filedialog, font
from PIL import Image, ImageTk
import webbrowser
import subprocess
import threading
import time
import os
import json
import requests

from src.planner import Waypoint, Itinerary
from src.export import export_to_pdf, export_to_json
from src.utils import is_valid_coordinate, format_coords, haversine_distance

import folium

def fetch_elevation(lat, lon):
    """Query OpenTopoData API to get ground elevation for a given coordinate."""
    try:
        response = requests.get(
            "https://api.opentopodata.org/v1/eudem25m",
            params={"locations": f"{lat},{lon}"},
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        return result["results"][0]["elevation"]
    except Exception as e:
        print(f"Elevation fetch failed: {e}")
        return None

class ExpeditionPlannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Arctic Expedition Planner")
        self.waypoints = []

        self.name_var = tk.StringVar()
        self.lat_var = tk.DoubleVar()
        self.lon_var = tk.DoubleVar()
        self.dist_var = tk.DoubleVar()
        self.speed_var = tk.DoubleVar()
        self.alt_var = tk.IntVar()
        self.manual_distance_enabled = tk.BooleanVar(value=False)

        mono_font = font.Font(family="Courier", size=10)

        # Title image
        image_path = os.path.join(os.path.dirname(__file__), "../assets/aep_gui_header.png")
        banner_image = Image.open(image_path)

        self.banner_photo = ImageTk.PhotoImage(banner_image)

        banner_label = tk.Label(root, image=self.banner_photo)
        banner_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))


        # Entry form layout
        tk.Label(root, text="Waypoint Name").grid(row=1, column=0, sticky="e", padx=(10, 2))
        tk.Entry(root, textvariable=self.name_var, width=25).grid(row=1, column=1, columnspan=2, sticky="w")

        tk.Label(root, text="Latitude").grid(row=2, column=0, sticky="e", padx=(10, 2))
        tk.Entry(root, textvariable=self.lat_var, width=25).grid(row=2, column=1, columnspan=2, sticky="w")

        tk.Label(root, text="Longitude").grid(row=3, column=0, sticky="e", padx=(10, 2))
        tk.Entry(root, textvariable=self.lon_var, width=25).grid(row=3, column=1, columnspan=2, sticky="w")

        tk.Label(root, text="Distance (km)").grid(row=4, column=0, sticky="e", padx=(10, 2))

        distance_frame = tk.Frame(root)
        distance_frame.grid(row=4, column=1, columnspan=2, sticky="w")

        self.distance_entry = tk.Entry(distance_frame, textvariable=self.dist_var, width=18, state='readonly')
        self.distance_entry.pack(side=tk.LEFT)

        tk.Checkbutton(distance_frame, text="Enter Distance Manaully", variable=self.manual_distance_enabled,
                       command=self.toggle_distance_field).pack(side=tk.LEFT, padx=8)

        tk.Label(root, text="Speed (kph)").grid(row=5, column=0, sticky="e", padx=(10, 2))
        tk.Entry(root, textvariable=self.speed_var, width=25).grid(row=5, column=1, columnspan=2, sticky="w")

        tk.Label(root, text="Altitude (m)").grid(row=6, column=0, sticky="e", padx=(10, 2))
        tk.Entry(root, textvariable=self.alt_var, width=25).grid(row=6, column=1, columnspan=2, sticky="w")

        # Button group
        button_frame = tk.Frame(root)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="Add Waypoint", command=self.add_waypoint).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Preview Map", command=self.preview_map).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Open Click Map", command=self.launch_map_server).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Add from Map Click", command=self.load_clicked_point).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export as JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export as PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)

        # Listbox headers
        headers = f"{'No.':<5} {'Name':<20} {'Coordinates':<30} {'Dist. from prev. WP (km)':>10}"
        tk.Label(root, text=headers, font=mono_font).grid(row=8, column=0, columnspan=3, sticky="w", padx=10)

        # Waypoint list frame with scrollbars
        list_frame = tk.Frame(root)
        list_frame.grid(row=9, column=0, columnspan=3, sticky="nsew")

        self.waypoint_listbox = tk.Listbox(
            list_frame,
            font=mono_font,
            height=8,
            width=100
        )
        self.waypoint_listbox.grid(row=0, column=0, sticky="nsew")

        yscroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.waypoint_listbox.yview)
        yscroll.grid(row=0, column=1, sticky="ns")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.waypoint_listbox.config(yscrollcommand=yscroll.set)
        self.waypoint_listbox.config(exportselection=False)

        # Waypoint control buttons
        wp_button_frame = tk.Frame(root)
        wp_button_frame.grid(row=10, column=0, columnspan=3, pady=5)
        tk.Button(wp_button_frame, text="Delete Waypoint", command=self.delete_waypoint).pack(side=tk.LEFT, padx=5)
        tk.Button(wp_button_frame, text="Move Up", command=self.move_waypoint_up).pack(side=tk.LEFT, padx=5)
        tk.Button(wp_button_frame, text="Move Down", command=self.move_waypoint_down).pack(side=tk.LEFT, padx=5)

        # Summary labels
        summary_frame = tk.Frame(root)
        summary_frame.grid(row=11, column=0, columnspan=3)
        self.total_distance_label = tk.Label(summary_frame, text="Total Distance: 0.0 km")
        self.total_distance_label.pack(pady=(10,0), anchor="center")

        self.total_time_label = tk.Label(summary_frame, text="Estimated Time: 0.0 hours")
        self.total_time_label.pack(pady=(0,10), anchor="center")


    def toggle_distance_field(self):
        """Enable or disable manual editing of the Distance field."""
        if self.manual_distance_enabled.get():
            self.distance_entry.config(state='normal')
        else:
            self.distance_entry.config(state='readonly')

    def add_waypoint(self):
        """Add a waypoint and calculate or accept distance."""
        lat = self.lat_var.get()
        lon = self.lon_var.get()

        if not (is_valid_coordinate(lat) and is_valid_coordinate(lon)):
            messagebox.showerror("Invalid Input", "Latitude or Longitude is out of valid range.")
            return

        if self.manual_distance_enabled.get():
            distance_km = self.dist_var.get()
        else:
            if self.waypoints:
                prev = self.waypoints[-1]
                distance_km = haversine_distance(prev.latitude, prev.longitude, lat, lon)
            else:
                distance_km = 0.0
            self.dist_var.set(distance_km)  # Only update the field in auto mode

        wp = Waypoint(
            name=self.name_var.get(),
            latitude=lat,
            longitude=lon,
            distance_km=distance_km,
            estimated_speed_kph=self.speed_var.get(),
            altitude_m=self.alt_var.get()
        )

        self.waypoints.append(wp)
        self.refresh_waypoint_list()

        # Confirm to user
        messagebox.showinfo("Waypoint Added", f"{wp.name} added with {distance_km:.2f} km from previous waypoint.")

        # Reset manual mode after adding
        self.manual_distance_enabled.set(False)
        self.toggle_distance_field()


    def refresh_waypoint_list(self):
        """Update the current itinerary and recalculate distances."""
        if not self.manual_distance_enabled.get():
            self.recalculate_distances()
        
        self.waypoint_listbox.delete(0, tk.END)

        for idx, wp in enumerate(self.waypoints):
            num = f"{idx+1:<5}"
            name = f"{wp.name:<20.20}"
            coords = f"({wp.latitude:.4f}, {wp.longitude:.4f})"
            coords = f"{coords:<30}"
            dist = f"{wp.distance_km:>10.2f}"
            line = f"{num}{name}{coords}{dist}"
            self.waypoint_listbox.insert(tk.END, line)

        self.update_summary()

    def recalculate_distances(self):
        """Recalculate distances the current itinerary."""
        for i, wp in enumerate(self.waypoints):
            if i == 0:
                wp.distance_km = 0.0
            else:
                prev = self.waypoints[i-1]
                wp.distance_km = haversine_distance(prev.latitude, prev.longitude, wp.latitude, wp.longitude)

    def delete_waypoint(self):
        """Delete a waypoint, updating the current itinerary and recalculating distances."""
        idx = self.waypoint_listbox.curselection()
        if not idx:
            messagebox.showwarning("No Selection", "Select a waypoint to delete.")
            return
        del self.waypoints[idx[0]]
        self.refresh_waypoint_list()

        self.update_summary()

    def move_waypoint_up(self):
        """Move a waypoint up one position in the current itinerary and recalculate distances."""
        idx = self.waypoint_listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        self.waypoints[i-1], self.waypoints[i] = self.waypoints[i], self.waypoints[i-1]
        self.refresh_waypoint_list()
        self.waypoint_listbox.selection_set(i-1)

        self.update_summary()

    def move_waypoint_down(self):
        """Move a waypoint down one position in the current itinerary and recalculate distances."""
        idx = self.waypoint_listbox.curselection()
        if not idx or idx[0] >= len(self.waypoints)-1:
            return
        i = idx[0]
        self.waypoints[i+1], self.waypoints[i] = self.waypoints[i], self.waypoints[i+1]
        self.refresh_waypoint_list()
        self.waypoint_listbox.selection_set(i+1)

        self.update_summary()

    def update_summary(self):
        """Update total distance and estimated travel time display."""
        total_distance = sum(wp.distance_km for wp in self.waypoints)
        total_time = 0.0
        for wp in self.waypoints:
            if wp.estimated_speed_kph > 0:
                total_time += wp.distance_km / wp.estimated_speed_kph

        self.total_distance_label.config(text=f"Total Distance: {total_distance:.2f} km")
        self.total_time_label.config(text=f"Estimated Time: {total_time:.2f} hours")

    def export_json(self):
        """Export itinerary to a JSON file using a Save As dialog."""
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            export_to_json(Itinerary(self.waypoints), filename)
            messagebox.showinfo("Export", "Exported itinerary to JSON.")

    def export_pdf(self):
        """Export current itinerary as a PDF file."""
        filename = filedialog.asksaveasfilename(defaultextension=".pdf")
        if filename:
            export_to_pdf(Itinerary(self.waypoints), filename)
            messagebox.showinfo("Export", "Exported itinerary to PDF.")

    def preview_map(self):
        """Generate interactive map with waypoints and polyline path."""
        if not self.waypoints:
            messagebox.showinfo("No Waypoints", "Add at least one waypoint to preview on the map.")
            return

        lat_center = self.waypoints[0].latitude
        lon_center = self.waypoints[0].longitude
        m = folium.Map(location=[lat_center, lon_center], zoom_start=7)

        points = []
        for wp in self.waypoints:
            folium.Marker(
                location=[wp.latitude, wp.longitude],
                popup=f"{wp.name}<br>{format_coords(wp.latitude, wp.longitude)}",
                tooltip=wp.name
            ).add_to(m)
            points.append([wp.latitude, wp.longitude])

        folium.PolyLine(points, color="blue", weight=3, opacity=0.7).add_to(m)

        map_path = "map.html"
        m.save(map_path)
        webbrowser.open(map_path)

    def launch_map_server(self):
        """Launch the Flask server for map clicks and open browser."""
        def start_server():
            subprocess.run(["python", "src/map_click_server.py"], check=False)

        threading.Thread(target=start_server, daemon=True).start()
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:5000")

    def load_clicked_point(self):
        """Load clicked coordinates and elevation, populate GUI fields."""
        if not os.path.exists("click_coords.json"):
            messagebox.showerror("No Click Data", "No clicked location found. Use the map first.")
            return

        with open("click_coords.json") as f:
            data = json.load(f)
        lat = float(data['latitude'])
        lon = float(data['longitude'])

        if not (is_valid_coordinate(lat) and is_valid_coordinate(lon)):
            messagebox.showerror("Invalid Coords", "Coordinates are not valid.")
            return

        self.lat_var.set(lat)
        self.lon_var.set(lon)

        elevation = fetch_elevation(lat, lon)
        if elevation is not None:
            self.alt_var.set(int(round(elevation)))
            messagebox.showinfo("Coordinates Loaded",
                f"Latitude and Longitude fields updated to: {lat}, {lon}\n"
                f"Estimated Altitude: {elevation} m")
        else:
            messagebox.showinfo("Coordinates Loaded",
                f"Latitude and Longitude fields updated to: {lat}, {lon}\n"
                f"(Elevation lookup failed)")

if __name__ == '__main__':
    root = tk.Tk()
    app = ExpeditionPlannerGUI(root)
    root.mainloop()
