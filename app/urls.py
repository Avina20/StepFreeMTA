from django.urls import path
from . import views

app_name = "app"
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("stations/", views.StationsView.as_view(), name="stations"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("save_favorite_route/", views.save_favorite_route, name="save_favorite_route"),
    path("stations/<int:station_id>/", views.station_detail, name="station_detail"),
    path("alerts/", views.alerts_view, name="alerts"),
]
