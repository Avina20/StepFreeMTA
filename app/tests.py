from django.test import TestCase, Client
from django.urls import reverse
from .models import Station, Review
from django.contrib.auth.models import User
from django.conf import settings
import json
from django.test import RequestFactory
from app.views import StationsView, StationDetailView


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
        self.assertEqual(response.url, reverse("maps:map_view"))


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
        self.assertEqual(response.url, reverse("maps:map_view"))


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


class StationsViewTest(TestCase):
    def setUp(self):
        # Create test data
        self.station1 = Station.objects.create(
            station_id=1,
            stop_name="Times Square",
            gtfs_stop_id="R01",
            complex_id=1,
            division="BMT",
            line="Astoria",
            borough="Q",
            cbd=True,
            daytime_routes="N W",
            structure="Elevated",
            gtfs_latitude=40.775036,
            gtfs_longitude=-73.912034,
            north_direction_label="Last Stop",
            south_direction_label="Manhattan",
            ada=True,
            ada_northbound=False,
            ada_southbound=True,
            georeference_latitude=40.775036,
            georeference_longitude=-73.912034,
            ada_notes="Elevator available at entrance.",
            computed_region_yamh_8v7k="123",
            computed_region_wbg7_3whc="456",
            computed_region_kjdx_g34t="789",
        )

        self.station2 = Station.objects.create(
            station_id=2,
            stop_name="Grand Central",
            gtfs_stop_id="R01",
            complex_id=1,
            division="BMT",
            line="Astoria",
            borough="Q",
            cbd=True,
            daytime_routes="N W",
            structure="Elevated",
            gtfs_latitude=40.775036,
            gtfs_longitude=-73.912034,
            north_direction_label="Last Stop",
            south_direction_label="Manhattan",
            ada=True,
            ada_northbound=False,
            ada_southbound=True,
            georeference_latitude=40.775036,
            georeference_longitude=-73.912034,
            ada_notes="Elevator available at entrance.",
            computed_region_yamh_8v7k="123",
            computed_region_wbg7_3whc="456",
            computed_region_kjdx_g34t="789",
        )

        self.station3 = Station.objects.create(
            station_id=3,
            stop_name="Union Square",
            gtfs_stop_id="R01",
            complex_id=1,
            division="BMT",
            line="Astoria",
            borough="Q",
            cbd=True,
            daytime_routes="N W",
            structure="Elevated",
            gtfs_latitude=40.775036,
            gtfs_longitude=-73.912034,
            north_direction_label="Last Stop",
            south_direction_label="Manhattan",
            ada=True,
            ada_northbound=False,
            ada_southbound=True,
            georeference_latitude=40.775036,
            georeference_longitude=-73.912034,
            ada_notes="Elevator available at entrance.",
            computed_region_yamh_8v7k="123",
            computed_region_wbg7_3whc="456",
            computed_region_kjdx_g34t="789",
        )

        self.factory = RequestFactory()

    def test_stations_view_all_stations(self):
        # Test that all stations are returned when no query is provided.
        request = self.factory.get(reverse("app:stations"))
        response = StationsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context_data["station_list"],
            [self.station2, self.station1, self.station3],  # Ordered alphabetically
            transform=lambda x: x,  # Avoid conversion to strings
        )

    def test_station_detail_view(self):
        # Test that the StationDetailView displays the correct station.
        url = reverse(
            "app:station_detail", kwargs={"station_id": self.station1.station_id}
        )
        request = self.factory.get(url)
        response = StationDetailView.as_view()(request, pk=self.station1.station_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["station"], self.station1)


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

    def test_go_from_button_redirect(self):
        # Test clicking the "Go" button and ensure correct redirection to map view with coordinates # noqa: E501
        station = Station.objects.get(gtfs_stop_id="R03")  # Example: Astoria Blvd
        response = self.client.get(reverse("app:station_detail", args=[station.id]))
        go_button_url = (
            reverse("maps:map_view")
            + f"?source_lat={station.gtfs_latitude}&source_lng={station.gtfs_longitude}&name={station.stop_name}"  # noqa: E501
        )
        self.assertContains(response, f'href="{go_button_url}"')

    def test_go_to_button_redirect(self):
        # Test clicking the "Go" button and ensure correct redirection to map view with coordinates # noqa: E501
        station = Station.objects.get(gtfs_stop_id="R03")  # Example: Astoria Blvd
        response = self.client.get(reverse("app:station_detail", args=[station.id]))
        go_button_url = (
            reverse("maps:map_view")
            + f"?dest_lat={station.gtfs_latitude}&dest_lng={station.gtfs_longitude}&name={station.stop_name}"  # noqa: E501
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
        User.objects.create_user(username="testuser2", password="password123")
        User.objects.create_user(username="testuser3", password="password123")
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

    def test_average_rating_calculation(self):
        self.client.login(username="testuser", password="password123")
        self.client.post(self.rate_url, {"rating": 4, "comment": ""})
        self.client.login(username="testuser2", password="password123")
        self.client.post(self.rate_url, {"rating": 3, "comment": ""})
        self.client.login(username="testuser3", password="password123")
        self.client.post(self.rate_url, {"rating": 5, "comment": ""})

        # Calculate the average rating manually
        expected_average = (4 + 3 + 5) / 3  # Should be 4.0

        # Get the average rating using the model method
        calculated_average = Review.get_average_rating(station_name=self.station)

        # Assert if the calculated average is correct
        self.assertEqual(calculated_average, expected_average)

    def test_average_rating_with_no_reviews(self):
        # Delete all reviews to test empty case
        Review.objects.all().delete()

        # The average rating should be 0 when there are no reviews
        self.assertEqual(Review.get_average_rating(station_name=self.station), 0)

    def test_average_rating_with_one_review(self):
        # Delete all reviews and add one review
        Review.objects.all().delete()
        self.client.login(username="testuser", password="password123")
        self.client.post(self.rate_url, {"rating": 5, "comment": ""})

        # The average rating should be the score of the single review
        self.assertEqual(Review.get_average_rating(station_name=self.station), 5)
