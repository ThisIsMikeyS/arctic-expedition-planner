"""
Handles exporting the itinerary to JSON and PDF formats.
"""

import json
import os
from dataclasses import asdict
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from src.planner import Itinerary

# FOR FUTURE IMPLEMENTATION OF MAP IMAGE INSIDE GENERATED PDF.
# def generate_map_image(itinerary, image_path="assets/route_map.png"):
#     """Create map centered on the first waypoint."""
#     start = itinerary.waypoints[0]
#     m = folium.Map(location=[start.latitude, start.longitude], zoom_start=7)

#     coords = []
#     for wp in itinerary.waypoints:
#         coords.append([wp.latitude, wp.longitude])
#         folium.Marker(
#             location=[wp.latitude, wp.longitude],
#             popup=wp.name,
#             tooltip=wp.name
#         ).add_to(m)

#     folium.PolyLine(coords, color="blue", weight=4).add_to(m)

#     map_html = "temp_map.html"
#     m.save(map_html)

#     # Convert to image
#     import imgkit
#     imgkit.from_file(map_html, image_path)

def export_to_json(itinerary, filename):
    """Export the given itinerary to a JSON file."""
    data = itinerary.to_dict()
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def export_to_pdf(itinerary, filename):
    """Export the given itinerary to a PDF file."""
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Draw the image at the top of the page
    image_path = os.path.join(os.path.dirname(__file__), "../assets/aep_gui_header.png")

    # Load image to get original size in pixels
    img = Image.open(image_path)
    img_width_px, img_height_px = img.size

    # Convert pixels to PDF points
    dpi = 72
    img_width_pt = img_width_px * 72 / dpi
    img_height_pt = img_height_px * 72 / dpi

    # Scale down to 50%
    scale = 0.5
    img_width_pt *= scale
    img_height_pt *= scale

    # Center the image at the top
    x = (width - img_width_pt) / 2
    y = height - img_height_pt - 40

    # Draw scaled image
    c.drawImage(image_path, x, y, width=img_width_pt, height=img_height_pt)

    # Move cursor below the image
    y_position = y - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y_position, "Arctic Expedition Itinerary")
    y_position -= 30

    # Draw expedition summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, f"Total Distance: {itinerary.total_distance():.2f} km")
    y_position -= 20
    c.drawString(50, y_position, f"Estimated Time: {itinerary.estimated_time():.2f} hours")
    y_position -= 30

    # Draw waypoint details
    c.setFont("Helvetica", 12)
    for i, wp in enumerate(itinerary.waypoints, 1):
        text = f"{i}. {wp.name} | Lat: {wp.latitude:.4f}, Lon: {wp.longitude:.4f} | " f"Distance: {wp.distance_km:.2f} km | Speed: {wp.estimated_speed_kph:.1f} kph | Alt: {wp.altitude_m} m"
        c.drawString(40, y_position, text)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 100
            c.setFont("Helvetica", 12)

    c.save()
