import googlemaps
from django.conf import settings
from django.shortcuts import render
from app.models import Review
from django.db.models import Avg
import json
import os
from math import radians, sin, cos, sqrt, atan2

# Load the accessible stations data from the 'data/accessiblemta.json' file
data_path = os.path.join(settings.BASE_DIR, "data", "accessiblemta.json")
with open(data_path, "r") as f:
    subway_data = json.load(f)

# Filter accessible subway stations
accessible_subway_data = [station for station in subway_data if station["ada"] == "1"]


def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate the distance between two coordinates
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(
        dlon / 2
    ) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def find_nearest_accessible_station(lat, lng, max_distance_km=10):
    nearest_station = None
    shortest_distance = float("inf")

    for station in subway_data:
        if station["ada"] == "1":  # Only consider accessible stations
            station_lat = float(station["gtfs_latitude"])
            station_lng = float(station["gtfs_longitude"])
            distance = calculate_distance(lat, lng, station_lat, station_lng)

            if distance <= max_distance_km and distance < shortest_distance:
                shortest_distance = distance
                nearest_station = station

    return nearest_station


def map_view(request):
    accessible_stations_with_reviews = []

    # Loop through accessible subway data
    for station in accessible_subway_data:
        station_reviews = Review.objects.filter(
            station__gtfs_stop_id=station["gtfs_stop_id"]
        ).order_by("-created_at")[
            :3
        ]  # Get the newest 3 reviews

        avg_rating = Review.objects.filter(
            station__gtfs_stop_id=station["gtfs_stop_id"]
        ).aggregate(Avg("rating"))["rating__avg"]

        # Append station data with reviews and rating
        accessible_stations_with_reviews.append(
            {
                **station,
                "reviews": [
                    {"user": review.user.username, "comment": review.comment}
                    for review in station_reviews
                ],
                "avg_rating": avg_rating or "No rating yet",
            }
        )

    context = {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        # "accessible_subway_data": accessible_subway_data,
        "accessible_stations_with_reviews": accessible_stations_with_reviews,
    }

    lat = request.GET.get("source_lat")
    lng = request.GET.get("source_lng")
    station_name = request.GET.get("name")
    dest_lat = request.GET.get("dest_lat")
    dest_lng = request.GET.get("dest_lng")

    # Restore context update for specific station
    if lat and lng and station_name:
        context.update({"lat": lat, "lng": lng, "station_name": station_name})

    if dest_lat and dest_lng:
        print(dest_lat + " " + dest_lng)
        context.update(
            {"dest_lat": dest_lat, "dest_lng": dest_lng, "station_name": station_name}
        )

    # Check if user location is provided and find nearest accessible station
    if lat and lng:
        user_lat = float(lat)
        user_lng = float(lng)
        nearest_station = find_nearest_accessible_station(user_lat, user_lng)
        print("Nearest accessible station found:", nearest_station)

        if nearest_station:
            context.update(
                {
                    "nearest_station_name": nearest_station["stop_name"],
                    "nearest_station_lat": nearest_station["gtfs_latitude"],
                    "nearest_station_lng": nearest_station["gtfs_longitude"],
                }
            )
        else:
            print("No accessible station found nearby.")
            context["nearest_station_error"] = "No accessible station found nearby."

    if request.method == "POST":
        start = request.POST.get("start")
        end = request.POST.get("end")

        print("Routing request from:", start, "to:", end)
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        try:
            # Fetch directions from Google Maps Directions API using transit mode
            directions_result = gmaps.directions(
                start, end, mode="transit", transit_mode="subway"
            )

            route_polyline = directions_result[0]["overview_polyline"]["points"]
            route_steps = directions_result[0]["legs"][0]["steps"]

            context.update(
                {
                    "route_polyline": route_polyline,
                    "route_steps": route_steps,
                    "start": start,
                    "end": end,
                }
            )

        except Exception as e:
            print("Error fetching directions:", str(e))
            context["error"] = str(e)

    return render(request, "map.html", context)
