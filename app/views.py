from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import generic
from django.conf import settings
from django.db.models import F
from .models import Station, Profile, Review
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, RatingForm
from django.utils import timezone
from django.http import JsonResponse
from google.transit import gtfs_realtime_pb2
import json
import requests
from django.core.exceptions import PermissionDenied
import datetime


# User Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect("maps:map_view")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create a profile for the user
            Profile.objects.create(user=user)

            login(request, user)
            messages.success(
                request, f"Account created successfully! Welcome, {user.username}!"
            )
            return redirect("maps:map_view")
        else:
            messages.error(request, "Registration failed. Please try again.")
    else:
        form = UserCreationForm()

    return render(request, "app/register.html", {"form": form})


# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect("maps:map_view")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request, f"Welcome, {user.username}! You are now logged in."
            )
            return redirect("maps:map_view")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "app/login.html", {"form": form})


# Logout View
@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("maps:map_view")
    else:
        raise PermissionDenied


# Stations View
class StationsView(generic.ListView):
    paginate_by = 10
    model = Station
    template_name = "app/stations.html"
    context_object_name = "station_list"

    def get_queryset(self):
        # Get the search query from the request
        query = self.request.GET.get("q")
        ada_filter = self.request.GET.get("ada_filter")

        # Start with all stations
        queryset = Station.objects.all().order_by(F("stop_name").asc())

        # Apply search filter if applicable
        if query:
            queryset = queryset.filter(stop_name__icontains=query)

        # Apply ADA filter based on the selected option
        if ada_filter == "fully":
            queryset = queryset.filter(ada=True)
        elif ada_filter == "partially":
            queryset = queryset.filter(ada_southbound=True, ada_northbound=False)
        elif ada_filter == "not":
            queryset = queryset.filter(ada=False)

        return queryset


# Station Detail View
class StationDetailView(generic.DetailView):
    model = Station
    template_name = "app/station_detail.html"


def station_detail(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    form = RatingForm(request.POST)

    already_reviewed = None

    if request.user.is_authenticated:
        user_reviewed = Review.objects.filter(
            station=station, user=request.user
        ).first()
        if user_reviewed:
            already_reviewed = True
        if request.method == "POST":
            if form.is_valid():
                if user_reviewed:
                    # Update the existing review
                    rating = user_reviewed
                    rating.rating = form.cleaned_data["rating"]
                    prev_comment = rating.comment
                    rating.comment = form.cleaned_data["comment"]
                    if rating.comment == "":
                        rating.comment = prev_comment
                    else:
                        rating.created_at = timezone.now()
                    rating.save()
                else:
                    rating = form.save(commit=False)
                    rating.station = station
                    rating.user = request.user
                    rating.created_at = timezone.now()
                    rating.save()
                messages.success(request, "Your review has been added!")
                return redirect("app:station_detail", station_id=station.id)
            else:
                print("Form errors: ", form.errors)
                messages.error(request, "Something went wrong")
        else:
            form = RatingForm(
                instance=user_reviewed
            )  # Pre-populate the form with the user's existing review (if any)

    ratings = station.rating.all()  # Get all ratings for this station
    # Calculate the average rating for this station

    avg_rating = Review.get_average_rating(station_name=station)

    # Find last 5 comments
    last_five_comments = (
        Review.objects.filter(comment__isnull=False, station=station)
        .exclude(comment="")
        .order_by("-created_at")[:5]
    )

    return render(
        request,
        "app/station_detail.html",
        {
            "station": station,
            "ratings": ratings,
            "comments": last_five_comments,
            "form": form,
            "avg_rating": avg_rating,
            "reviewed": already_reviewed,
        },
    )


class ProfileView(generic.DetailView):
    model = Profile
    template_name = "app/profile.html"
    context_object_name = "profile"

    def get_object(self):
        return self.request.user.profile


def alerts_view(request):
    # Get selected lines from the request
    selected_lines = request.GET.get("lines", "")
    lines_list = selected_lines.split(",") if selected_lines else []

    search_patterns = [f"[{line}]" for line in lines_list]

    url = (
        "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"
    )
    try:
        response = requests.get(url)

        # Decode the Protobuf data
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        # Extract and format alert data
        alerts_data = []
        for entity in feed.entity:
            if entity.HasField("alert"):
                alert = entity.alert

                header = (
                    alert.header_text.translation[0].text
                    if alert.header_text.translation
                    else ""
                )
                description = (
                    alert.description_text.translation[0].text
                    if alert.description_text.translation
                    else ""
                )

                # If lines are selected, filter based on the content
                if lines_list:
                    # Check if any of the search patterns are in the header
                    if any(pattern in header for pattern in search_patterns):
                        # Include this alert
                        alerts_data.append(
                            {
                                "header": header,
                                "description": description,
                            }
                        )
                else:
                    # No lines selected, include all alerts
                    alerts_data.append(
                        {
                            "header": header,
                            "description": description,
                        }
                    )

    except Exception as e:
        alerts_data = None
        print("Error fetching alerts data:", e)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"alerts_data": alerts_data})
    return render(request, "app/alerts.html", {"alerts_data": alerts_data})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        date = request.POST.get("birth_date")
        if date > datetime.date.today().isoformat():
            messages.error(request, "Invalid date")
            return redirect("app:edit_profile")
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("app:profile")
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        "form": form,
    }

    return render(request, "app/edit_profile.html", context)


@login_required
def save_favorite_route(request):
    if request.method == "POST":
        data = json.loads(request.body)
        start = data.get("start")
        end = data.get("end")

        print(start)
        profile = request.user.profile
        profile.fav_source_latitude = start["lat"]
        profile.fav_source_longitude = start["lng"]
        profile.fav_dest_latitude = end["lat"]
        profile.fav_dest_longitude = end["lng"]
        profile.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})
