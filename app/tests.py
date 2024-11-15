from django.test import TestCase, Client
from django.urls import reverse
from .models import Station, Review
from django.contrib.auth.models import User
from django.conf import settings
import json


class LoginViewTest(TestCase):
    def setUp(self):
        self.url = reverse("app:login")
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()

    def test_login_view_get(
        self,
    ):  # accessed via a GET request, check status code is 200 and correct template (app/login.html) is used # noqa: E501
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/login.html")

    def test_login_view_post_success(
        self,
    ):  # It asserts that the response redirects the user to the map view upon successful login # noqa: E501
        response = self.client.post(
            self.url, {"username": "testuser", "password": "password"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("maps:map_view"))

    def test_login_view_post_failure(
        self,
    ):  # simulates a login attempt with incorrect credentials via a POST request, asserts that the page reloads (status code 200) and checks for the presence of the error message # noqa: E501
        response = self.client.post(
            self.url, {"username": "wronguser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        # Instead of asserting form error, check for error message presence
        self.assertContains(response, "Please enter a correct username and password.")

    def test_access_login_view_after_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('maps:map_view'))


class RegisterViewTest(TestCase):
    def setUp(self):
        self.url = reverse("app:register")
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword@1234"
        )

    def test_register_view_get(
        self,
    ):  # accessed via a GET request, check status code is 200 and correct template (app/register.html) is used # noqa: E501
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/register.html")

    def test_register_view_post_success(
        self,
    ):  # simulates a registration attempt with valid data (matching passwords) and redirects the user to the map view upon successful registtration # noqa: E501
        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "password1": "testpassword",
                "password2": "testpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("maps:map_view"))

    def test_register_view_post_failure(
        self,
    ):  # simulates a registration attempt where the two password fields do not match
        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "password1": "testpassword",
                "password2": "differentpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        # Instead of asserting form error, check for error message presence
        self.assertContains(response, "The two password fields didn’t match.")
        
    def test_access_register_view_after_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('maps:map_view'))
        
        
class LogoutTest(TestCase):
    def setUp(self):
        self.url = reverse("app:logout")
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        
    def test_logout_post(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class StationsAccessibilityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Load stations from accessiblemta.json
        with open(settings.BASE_DIR / "data/accessiblemta.json", "r") as f:
            stations_data = json.load(f)

        # Create station objects in the test database
        for station in stations_data:
            Station.objects.create(
                gtfs_stop_id=station["gtfs_stop_id"],
                station_id=station["station_id"],
                complex_id=station["complex_id"],
                division=station["division"],
                line=station["line"],
                stop_name=station["stop_name"],
                borough=station["borough"],
                cbd=station["cbd"] == "TRUE",
                daytime_routes=station["daytime_routes"],
                structure=station["structure"],
                gtfs_latitude=float(station["gtfs_latitude"]),
                gtfs_longitude=float(station["gtfs_longitude"]),
                ada=station["ada"] == "1",
                ada_northbound=station["ada_northbound"] == "1",
                ada_southbound=station["ada_southbound"] == "1",
                georeference_latitude=float(station["georeference"]["coordinates"][1]),
                georeference_longitude=float(station["georeference"]["coordinates"][0]),
            )

    def test_station_accessibility(self):
        # Test for a station marked as accessible
        station = Station.objects.get(
            gtfs_stop_id="R03"
        )  # Example: Astoria Blvd is ADA accessible
        response = self.client.get(reverse("app:station_detail", args=[station.id]))
        self.assertContains(response, "Accessible: True")

        # Test for a station not marked as accessible
        station = Station.objects.get(
            gtfs_stop_id="R01"
        )  # Example: Astoria-Ditmars Blvd is not ADA accessible
        response = self.client.get(reverse("app:station_detail", args=[station.id]))
        self.assertContains(response, "Accessible: False")

    def test_go_button_redirect(self):
        # Test clicking the "Go" button and ensure correct redirection to map view with coordinates # noqa: E501
        station = Station.objects.get(gtfs_stop_id="R03")  # Example: Astoria Blvd
        response = self.client.get(reverse("app:station_detail", args=[station.id]))
        print(response)
        go_button_url = (
            reverse("maps:map_view")
            + f"?source_lat={station.gtfs_latitude}&source_lng={station.gtfs_longitude}&name={station.stop_name}"  # noqa: E501
        )
        self.assertContains(response, f'href="{go_button_url}"')


class ReviewTests(TestCase):
    # Create station database for testing purposes
    @classmethod
    def setUpTestData(cls):
        # Load stations from accessiblemta.json
        with open(settings.BASE_DIR / "data/accessiblemta.json", "r") as f:
            stations_data = json.load(f)

        # Create station objects in the test database
        for station in stations_data:
            Station.objects.create(
                gtfs_stop_id=station["gtfs_stop_id"],
                station_id=station["station_id"],
                complex_id=station["complex_id"],
                division=station["division"],
                line=station["line"],
                stop_name=station["stop_name"],
                borough=station["borough"],
                cbd=station["cbd"] == "TRUE",
                daytime_routes=station["daytime_routes"],
                structure=station["structure"],
                gtfs_latitude=float(station["gtfs_latitude"]),
                gtfs_longitude=float(station["gtfs_longitude"]),
                ada=station["ada"] == "1",
                ada_northbound=station["ada_northbound"] == "1",
                ada_southbound=station["ada_southbound"] == "1",
                georeference_latitude=float(station["georeference"]["coordinates"][1]),
                georeference_longitude=float(station["georeference"]["coordinates"][0]),
            )

    def setUp(self):
        # Create a test user and a test station
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.station = Station.objects.get(gtfs_stop_id="R03")
        self.rate_url = reverse("app:station_detail", args=[self.station.id])

    def test_leave_new_review(self):
        # Log in the test user
        self.client.login(username="testuser", password="password123")

        # Submit a new review with a rating of 4
        response = self.client.post(self.rate_url, {"rating": 4})

        # Check if the rating was created
        rating = Review.objects.filter(user=self.user, station=self.station).first()
        self.assertIsNotNone(rating)  # Ensure the rating was created
        self.assertEqual(rating.rating, 4)  # Check that the rating value is correct
        self.assertEqual(
            response.status_code, 302
        )  # Check for a redirect after success

    def test_leave_new_comment(self):
        # Log in the test user
        self.client.login(username="testuser", password="password123")

        # Submit a new comment 'Nice station'
        response = self.client.post(
            self.rate_url, {"rating": 4, "comment": "Nice station"}
        )

        # Check that commnet was created
        rating = Review.objects.filter(user=self.user, station=self.station).first()
        self.assertIsNotNone(rating)  # Ensure rating with comment was created
        self.assertEqual(rating.comment, "Nice station")  # Ensure comment is correct
        self.assertEqual(response.status_code, 302)

    def test_update_existing_review(self):
        # Log in the test user and leave an initial review
        self.client.login(username="testuser", password="password123")
        Review.objects.create(
            user=self.user, station=self.station, rating=3
        )  # Initial rating

        # Submit a new review with a different rating value
        response = self.client.post(self.rate_url, {"rating": 5})

        # Check that the existing review was updated
        rating = Review.objects.get(user=self.user, station=self.station)
        self.assertEqual(rating.rating, 5)  # Ensure the rating was updated to 5
        self.assertEqual(
            response.status_code, 302
        )  # Check for a redirect after success

    def test_update_existing_comment(self):
        # Log in the test user and leave an initial review
        self.client.login(username="testuser", password="password123")
        Review.objects.create(
            user=self.user, station=self.station, rating=3, comment="OK station"
        )  # Initial rating

        # Submit a new review with a different rating value
        response = self.client.post(
            self.rate_url, {"rating": 5, "comment": "Perfect station"}
        )

        # Check that the existing review was updated
        rating = Review.objects.get(user=self.user, station=self.station)
        self.assertEqual(
            rating.comment, "Perfect station"
        )  # Ensure the rating was updated to 5
        self.assertEqual(
            response.status_code, 302
        )  # Check for a redirect after success

    def test_update_review_keep_comment(self):
        self.client.login(username="testuser", password="password123")
        Review.objects.create(
            user=self.user, station=self.station, rating=3, comment="OK station"
        )  # Initial rating

        # Submit a new review with a different rating value and no new comment
        response = self.client.post(self.rate_url, {"rating": 5, "comment": ""})

        # Check that the existing review was updated
        rating = Review.objects.get(user=self.user, station=self.station)
        self.assertEqual(
            rating.comment, "OK station"
        )  # Ensure the rating was updated to 5 and comment isn't changed
        self.assertEqual(
            response.status_code, 302
        )  # Check for a redirect after success
