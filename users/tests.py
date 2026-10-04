from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserApiTests(APITestCase):
    """
    APITestCase is Django's TestCase with conveniences for calling API
    endpoints (`self.client.get/post/...`).

    Each test method runs against a fresh, empty test database, so tests never
    depend on each other or on your dev data.
    """

    def setUp(self) -> None:
        # Runs before every test method below.
        self.john = User.objects.create(name="John", email="john@example.com")

    def test_get_all_users(self) -> None:
        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["users"]), 1)
        self.assertEqual(response.data["users"][0]["email"], "john@example.com")

    def test_get_one_user(self) -> None:
        response = self.client.get(f"/api/users/{self.john.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "John")

    def test_get_nonexistent_user_returns_404(self) -> None:
        response = self.client.get("/api/users/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_valid_user_creates_user(self) -> None:
        payload = {"name": "Alice", "email": "alice@example.com"}

        # format="json" sends a JSON body, which fills request.data.
        response = self.client.post("/api/users/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())

    def test_post_invalid_user_returns_400(self) -> None:
        # `name` is missing and `email` is not a valid address.
        payload = {"email": "not-an-email"}

        response = self.client.post("/api/users/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)   # required field
        self.assertIn("email", response.data)  # invalid format

    def test_post_duplicate_email_returns_400(self) -> None:
        # john@example.com was already created in setUp().
        payload = {"name": "Johnny", "email": "john@example.com"}

        response = self.client.post("/api/users/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)  # uniqueness validation

    def test_filter_users_by_query_parameter(self) -> None:
        User.objects.create(name="Jane", email="jane@example.com")

        # The dict is turned into a query string: /api/users/?name=Jane
        response = self.client.get("/api/users/", {"name": "Jane"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["users"]), 1)
        self.assertEqual(response.data["users"][0]["name"], "Jane")
