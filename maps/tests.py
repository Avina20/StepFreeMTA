# from django.test import TestCase, Client
# from django.urls import reverse
# from unittest.mock import patch
# from django.conf import settings
# from django.contrib.auth.models import User


# class MapsViewTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse("maps:map_view")
#         self.valid_data = {
#             "start": "Times Square, New York, NY",
#             "end": "Central Park, New York, NY",
#         }

#     def test_template_used(self):
#         """Test that the map template is rendered correctly."""
#         response = self.client.get(self.url)
#         self.assertTemplateUsed(response, "map.html")
#         self.assertEqual(response.status_code, 200)

#     @patch("googlemaps.Client.directions")
#     def test_directions_success(self, mock_directions):
#         """Test the successful retrieval of directions."""
#         mock_directions.return_value = [
#             {
#                 "overview_polyline": {"points": "mock_polyline"},
#                 "legs": [
#                     {
#                         "steps": [
#                             {
#                                 "distance": {"text": "0.1 mi"},
#                                 "instructions": "Head north",
#                             }
#                         ]
#                     }
#                 ],
#             }
#         ]

#         response = self.client.post(self.url, self.valid_data)
#         mock_directions.assert_called_once_with(
#             "Times Square, New York, NY",
#             "Central Park, New York, NY",
#             mode="transit",
#             transit_mode="subway",
#         )

#         self.assertEqual(response.context["route_polyline"], "mock_polyline")
#         self.assertEqual(len(response.context["route_steps"]), 1)
#         self.assertEqual(
#             response.context["route_steps"][0]["distance"]["text"], "0.1 mi",
#         )

#     @patch("googlemaps.Client.directions")
#     def test_directions_api_error(self, mock_directions):
#         """Test that API errors are handled properly."""
#         mock_directions.side_effect = Exception("API Error")
#         response = self.client.post(self.url, self.valid_data)
#         self.assertIn("error", response.context)
#         self.assertEqual(response.context["error"], "API Error")

#     def test_missing_start_or_end(self):
#         """Test that missing start or end location returns an error."""
#         response = self.client.post(
#             self.url, {"start": "", "end": "Central Park, New York, NY"}
#         )
#         self.assertContains(
#             response, "Please enter both a starting point and an ending point."
#         )

#         response = self.client.post(
#             self.url, {"start": "Times Square, New York, NY", "end": ""}
#         )
#         self.assertContains(
#             response, "Please enter both a starting point and an ending point."
#         )

#     def test_google_maps_api_key_in_context(self):
#         """Test that the Google Maps API key is passed to the template context."""
#         response = self.client.get(self.url)
#         self.assertEqual(
#             response.context["google_maps_api_key"], settings.GOOGLE_MAPS_API_KEY
#         )


# class ButtonsTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse("maps:map_view")
#         self.login_url = reverse("app:login")
#         self.register_url = reverse("app:register")
#         self.user = User.objects.create_user(username="testuser", password="password")

#     def test_login_button_exists(self):
#         """Checks that the login button exists with the correct class."""
#         response = self.client.get(self.url)
#         self.assertContains(
#             response,
#             (
#                 '<a class="nav-link" href="{}">'
#                 '<i class="bi bi-box-arrow-in-right"></i> Login</a>'
#             ).format(self.login_url),
#             html=True,
#         )

#     def test_register_button_exists(self):
#         """Checks that the register button exists with the correct class."""
#         response = self.client.get(self.url)
#         self.assertContains(
#             response,
#             (
#                 '<a class="nav-link" href="{}">'
#                 '<i class="bi bi-person-plus"></i> Register</a>'
#             ).format(self.register_url),
#             html=True,
#         )

#     def test_logout_button_exists(self):
#         """Checks that the logout button exists for authenticated users."""
#         self.client.login(username="testuser", password="password")
#         response = self.client.get(self.url)
#         self.assertContains(
#             response,
#             (
#                 '<button type="submit" class="btn btn-danger">'
#                 '<i class="bi bi-box-arrow-right"></i> Logout</button>'
#             ),
#             html=True,
#         )
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth.models import User


class MapsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("maps:map_view")
        self.valid_data = {
            "start": "Times Square, New York, NY",
            "end": "Central Park, New York, NY",
        }

    def test_template_used(self):
        """Test that the map template is rendered correctly."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "map.html")
        self.assertEqual(response.status_code, 200)

    @patch("googlemaps.Client.directions")
    def test_directions_success(self, mock_directions):
        """Test the successful retrieval of directions."""
        mock_directions.return_value = [
            {
                "overview_polyline": {"points": "mock_polyline"},
                "legs": [
                    {
                        "steps": [
                            {
                                "distance": {"text": "0.1 mi"},
                                "instructions": "Head north",
                            }
                        ]
                    }
                ],
            }
        ]

        response = self.client.post(self.url, self.valid_data)
        mock_directions.assert_called_once_with(
            "Times Square, New York, NY",
            "Central Park, New York, NY",
            mode="transit",
            transit_mode="subway",
        )

        self.assertEqual(response.context["route_polyline"], "mock_polyline")
        self.assertEqual(len(response.context["route_steps"]), 1)
        self.assertEqual(
            response.context["route_steps"][0]["distance"]["text"], "0.1 mi"
        )

    @patch("googlemaps.Client.directions")
    def test_directions_api_error(self, mock_directions):
        """Test that API errors are handled properly."""
        mock_directions.side_effect = Exception("API Error")
        response = self.client.post(self.url, self.valid_data)
        self.assertIn("error", response.context)
        self.assertEqual(response.context["error"], "API Error")

    def test_missing_start_or_end(self):
        """Test that missing start or end location returns an error."""
        response = self.client.post(
            self.url, {"start": "", "end": "Central Park, New York, NY"}
        )
        self.assertContains(
            response, "Please enter both a starting point and an ending point."
        )

        response = self.client.post(
            self.url, {"start": "Times Square, New York, NY", "end": ""}
        )
        self.assertContains(
            response, "Please enter both a starting point and an ending point."
        )

    def test_google_maps_api_key_in_context(self):
        """Test that the Google Maps API key is passed to the template context."""
        response = self.client.get(self.url)
        self.assertEqual(
            response.context["google_maps_api_key"], settings.GOOGLE_MAPS_API_KEY
        )


class ButtonsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("maps:map_view")
        self.login_url = reverse("app:login")
        self.register_url = reverse("app:register")
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_login_button_exists(self):
        """Checks that the login button exists with the correct class."""
        response = self.client.get(self.url)
        self.assertContains(
            response,
            (
                '<a class="nav-link" href="{}">'
                '<i class="bi bi-box-arrow-in-right"></i> Login</a>'
            ).format(self.login_url),
            html=True,
        )

    def test_register_button_exists(self):
        """Checks that the register button exists with the correct class."""
        response = self.client.get(self.url)
        self.assertContains(
            response,
            (
                '<a class="nav-link" href="{}">'
                '<i class="bi bi-person-plus"></i> Register</a>'
            ).format(self.register_url),
            html=True,
        )

    def test_logout_button_exists(self):
        """Checks that the logout button exists for authenticated users."""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertContains(
            response,
            (
                '<button type="submit" class="btn btn-danger">'
                '<i class="bi bi-box-arrow-right"></i> Logout</button>'
            ),
            html=True,
        )
