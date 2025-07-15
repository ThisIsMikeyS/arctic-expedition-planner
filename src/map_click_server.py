from flask import Flask, request, render_template_string
import json

app = Flask(__name__)

MAP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
  <title>Click to Add Waypoint</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
</head>
<body>
<h2>Click the map to select coordinates</h2>
<div id="map" style="height: 90vh;"></div>
<script>
var map = L.map('map').setView([69.65, 18.95], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
}).addTo(map);
map.on('click', function(e) {
  let lat = e.latlng.lat.toFixed(5);
  let lon = e.latlng.lng.toFixed(5);
  fetch('/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude: lat, longitude: lon })
  }).then(() => alert('Coordinates sent: ' + lat + ", " + lon));
});
</script>
</body>
</html>
'''

@app.route('/')
def map_page():
    """Serves an HTML page with a map."""
    return render_template_string(MAP_TEMPLATE)

@app.route('/add', methods=['POST'])
def add():
    """Receives coordinates and stores them in a file."""
    coord = request.json
    with open("click_coords.json", "w") as f:
        json.dump(coord, f)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)