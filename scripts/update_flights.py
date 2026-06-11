import json
import requests
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "Web_Map" / "data" / "flights.geojson"

URL = "https://opensky-network.org/api/states/all"

PARAMS = {
    "lamin": 58,
    "lamax": 84,
    "lomin": -75,
    "lomax": -5
}

def main():
    response = requests.get(URL, params=PARAMS, timeout=40)
    response.raise_for_status()

    data = response.json()
    features = []

    for flight in data.get("states", []) or []:
        lon = flight[5]
        lat = flight[6]

        if lon is None or lat is None:
            continue

        altitude_m = flight[7]
        velocity_mps = flight[9]

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "callsign": flight[1].strip() if flight[1] else "UNKNOWN",
                "country": flight[2],
                "altitude_ft": round(altitude_m * 3.28084) if altitude_m else None,
                "speed_kmh": round(velocity_mps * 3.6) if velocity_mps else None,
                "heading": flight[10],
                "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(geojson, file, indent=2)

    print(f"Saved {len(features)} flights.")

if __name__ == "__main__":
    main()