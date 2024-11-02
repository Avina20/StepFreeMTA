# admin_panel/urls.py
from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("users/", views.user_list, name="user-list"),
    path("users/delete/<int:user_id>/", views.delete_user, name="delete-user"),
]
