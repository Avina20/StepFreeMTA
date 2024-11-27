from django import forms
from .models import Profile, Review


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
            "home_address",
            "work_address",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "fav_station": forms.Select(),  # Dropdown for stations,
            "home_address": forms.TextInput(
                attrs={
                    "placeholder": "Enter home location",
                    "onchange": "resetHomeLocation()",
                }
            ),
            "work_address": forms.TextInput(
                attrs={
                    "placeholder": "Enter work location",
                    "onchange": "resetWorkLocation()",
                }
            ),
        }

    def clean_home_latitude(self):
        lat = self.cleaned_data.get("home_latitude")
        if lat is not None and lat != "":
            if lat < -90 or lat > 90:
                raise forms.ValidationError("Home latitude must be between -90 and 90.")
        return lat

    def clean_home_longitude(self):
        lon = self.cleaned_data.get("home_longitude")
        if lon is not None and lon != "":
            if lon < -180 or lon > 180:
                raise forms.ValidationError(
                    "Home longitude must be between -180 and 180."
                )
        return lon

    def clean_work_latitude(self):
        lat = self.cleaned_data.get("work_latitude")
        if lat is not None and lat != "":
            if lat < -90 or lat > 90:
                raise forms.ValidationError("Work latitude must be between -90 and 90.")
        return lat

    def clean_work_longitude(self):
        lon = self.cleaned_data.get("work_longitude")
        if lon is not None and lon != "":
            if lon < -180 or lon > 180:
                raise forms.ValidationError(
                    "Work longitude must be between -180 and 180."
                )
        return lon


class RatingForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
