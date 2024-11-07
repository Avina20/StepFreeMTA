from django import forms
from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "birth_date",
            "home_latitude",
            "home_longitude",
            "work_latitude",
            "work_longitude",
            "fav_station",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "fav_station": forms.Select(),  # Dropdown for stations
        }
