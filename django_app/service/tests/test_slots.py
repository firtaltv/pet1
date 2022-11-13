from service.models import Slot
from users.models import User
from rest_framework import status
from django.urls import reverse
from users.tests.tests import UserBase
from typing import List


class ScheduleTest(UserBase):
    fixtures = [
        'users/tests/fixtures/user_fixtures.json',
        'service/tests/fixtures/schedule_fixtures.json',
        'service/tests/fixtures/slots_fixtures.json',
    ]

    def setUp(self) -> None:
        super().setUp()
        self.create_schedule_as_admin_data = self.get_from_fixture(
            'service/tests/fixtures/create_schedule_as_admin_fixture.json'
        )
        self.create_schedule_as_therapist_data = self.get_from_fixture(
            'service/tests/fixtures/create_schedule_as_therapist_fixture.json'
        )
        self.create_schedule_as_client_data = self.get_from_fixture(
            'service/tests/fixtures/create_schedule_as_client_fixture.json'
        )

    def test_get_therapist_schedule(self):
        expected_data = {
            'pk': 1001,
            "days": ['1', '3'],
            'therapist':
                {
                    'pk': 1001,
                    'last_name': '',
                    'first_name': ''
                },
            "start_time": "11:00:00",
            "end_time": "16:00:00",
            "valid_from": "2022-09-09",
            "valid_to": "2022-10-09",
            "force_create": True
        }
        url = reverse('service:therapist_schedule_object', kwargs={'pk': self.admin_user.id})
        self.client.force_login(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)
        self.assertDictEqual(dict(response.data), expected_data)

    def test_create_schedule_admin(self):
        expected_data = ['2022-09-14', '2022-09-21', '2022-09-28', '2022-10-05']
        response = self.response_create_schedule(user=self.admin_user, data=self.create_schedule_as_admin_data[0])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['updated_slot_dates'], [])
        self.assertEqual(len(response.data['created_slot_dates']), 4)
        self.assertListEqual(response.data['created_slot_dates'], expected_data)
        self.assertEqual(len(list(Slot.objects.all())), 8)

    def test_create_conflict_schedule_admin(self):
        expected_data = ['2022-09-15', '2022-09-22', '2022-09-29', '2022-10-06']
        response = self.response_create_schedule(user=self.admin_user, data=self.create_schedule_as_admin_data[1])
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertListEqual(response.data['slots_occupied_dates'], expected_data)
        self.assertEqual(len(list(Slot.objects.all())), 4)

    def test_create_schedule_admin_force_create(self):
        pass

    def test_create_schedule_therapist(self):
        expected_data = ['2022-09-09', '2022-09-16', '2022-09-23', '2022-09-30', '2022-10-07']
        response = self.response_create_schedule(user=self.therapist_1, data=self.create_schedule_as_therapist_data[0])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['updated_slot_dates'], [])
        self.assertEqual(len(response.data['created_slot_dates']), 5)
        self.assertListEqual(response.data['created_slot_dates'], expected_data)
        self.assertEqual(len(list(Slot.objects.all())), 9)

    def test_create_conflict_schedule_therapist(self):
        expected_data = ['2022-09-15', '2022-09-22', '2022-09-29', '2022-10-06']
        response = self.response_create_schedule(user=self.therapist_2, data=self.create_schedule_as_therapist_data[1])
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertListEqual(response.data['slots_occupied_dates'], expected_data)
        self.assertEqual(len(list(Slot.objects.all())), 4)

    def test_create_schedule_therapist_force_create(self):
        pass

    def response_create_schedule(self, user: User, data: List[dict]):
        url = reverse('service:therapist_schedule_create')
        self.client.force_login(user=user)
        response = self.client.post(url, data=data)
        return response
