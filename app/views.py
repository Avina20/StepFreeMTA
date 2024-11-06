from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import generic
from django.db.models import F
from .models import Station, Profile
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from django.http import JsonResponse
from google.transit import gtfs_realtime_pb2
import json
import requests


# User Registration View
def register_view(request):
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
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect("maps:map_view")


# Stations View
class StationsView(generic.ListView):
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

@login_required
def station_detail(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    form = RatingForm(request.POST)

    # Check if the user has already reviewed this station
    user_reviewed = Review.objects.filter(station=station, user=request.user).first()

    if request.method == "POST":
        if form.is_valid():
            if user_reviewed:
                # Update the existing review
                rating = user_reviewed
                rating.rating = form.cleaned_data["rating"]
                rating.save()
            else:
                rating = form.save(commit=False)
                rating.station = station
                rating.user = request.user
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
    if ratings is None:
        avg_rating = 0
    else:
        avg_rating = Review.objects.filter(station=station).aggregate(Avg("rating"))[
            "rating__avg"
        ]

    return render(
        request,
        "app/station_detail.html",
        {
            "station": station,
            "ratings": ratings,
            "form": form,
            "avg_rating": avg_rating,
        },
    )


class ProfileView(generic.DetailView):
    model = Profile
    template_name = "app/profile.html"
    context_object_name = "profile"

    def get_object(self):
        return self.request.user.profile


def alerts_view(request):
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
                informed_entities = []
                for informed_entity in alert.informed_entity:
                    informed_entities.append(
                        {
                            "route_id": informed_entity.route_id,
                            "stop_id": informed_entity.stop_id,
                        }
                    )
                header = (
                    alert.header_text.translation[0].text
                    if alert.header_text.translation
                    else None
                )
                description = (
                    alert.description_text.translation[0].text
                    if alert.description_text.translation
                    else None
                )
                alerts_data.append(
                    {
                        "header": header,
                        "description": description,
                        "informed_entities": informed_entities,
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
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("app:profile")  # Change to your profile page URL name
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "app/edit_profile.html", {"form": form})


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
