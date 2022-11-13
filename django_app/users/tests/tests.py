import json

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User


class UserBase(APITestCase):
    fixtures = ['users/tests/fixtures/user_fixtures.json', ]

    @staticmethod
    def get_from_fixture(fixture_path):
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def setUp(self) -> None:
        self.admin_user = User.objects.get(id=1001)
        self.therapist_1 = User.objects.get(id=1002)
        self.therapist_2 = User.objects.get(id=1003)
        self.client_1 = User.objects.get(id=1004)

    """ In development """
    def test_get_user_as_admin_user(self):
        expected_data = {
            "pk": 1001,
            "username": "admin",
            "first_name": "",
            "last_name": "",
            "email": "admin@email.com",
            "profile_photo": None
        }
        url = reverse('users:user_profile')
        self.client.force_login(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    # def test_edit_user(self):
    #     url = reverse('users:user_profile')
    #     self.client.force_login(user=self.admin_user)
    #     response = self.client.patch(url, {'first_name': 'Philip', 'email': 'admin1@email.com'})
    #     self.assertEqual(response.data['first_name'], 'Philip')
    #     self.assertEqual(response.data['email'], self.admin_user.email)
