from django.test.client import Client
from django.core.urlresolvers import reverse_lazy

from ...utils.tests.test_base import BaseTestCase
from ..models import CaspUser


class UserViewTestCases(BaseTestCase):

    def setUp(self):
        self.user_client = self.create_user_and_login()
        self.anonymous_client = Client()

    def test_login_user(self):
        """
        Test to login a user
        """
        response = self.client.post(reverse_lazy('login'), data={
            "username": self.email,
            "password": self.password
        })
        self.assertEqual(response.status_code, 200)

    def test_access_profile(self):
        """
        Tests that the user can access the profile page
        """
        response = self.user_client.get(reverse_lazy('profile_detail'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_access(self):
        """
        Tests that a user can access to edit his profile
        """
        response = self.user_client.get(reverse_lazy('profile_update'))
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        """
        tests that the user can update his profile.
        """
        current_user = CaspUser.objects.get(id=self.user.id)
        update_email = "jane@example.com"
        current_email = current_user.email

        self.assertNotEqual(current_user.email, update_email)

        response = self.user_client.post(reverse_lazy('profile_update'), data={
            "username": current_user.username,
            "email": update_email,
            "phone": current_user.phone
        })
        self.assertEqual(response.status_code, 302)

        updated_user = CaspUser.objects.get(id=self.user.id)
        self.assertEqual(updated_user.email, update_email)
        self.assertNotEqual(updated_user.email, current_email)
