from ...utils.tests.test_base import BaseTestCase
from ..models import CaspUser


class CaspUserModelTestCases(BaseTestCase):

    def setUp(self):
        self.email = 'jpueblo@example.com'
        self.password = 'abc123'

        self.user_client = self.create_user_and_login()

    def test_custom_user_model_should_have_expected_number_of_fields(self):
        """
        Tests the expected number of fields in custom User model.
        """
        self.assertEqual(len(self.user._meta.fields), 12)

    def test_create_user(self):
        """
        Tests that a user can be created in the database.
        """
        email = "grivera@example.com"
        CaspUser.objects.create_user(
            username="grivera",
            email=email,
            password=self.password,
            first_name="Gabo",
            last_name="Rivera",
            phone="555-555-5555"
        )
        self.assertTrue(CaspUser.objects.filter(email=email).exists())
        self.assertTrue(CaspUser.objects.filter(email=email).count() == 1)

    def test_create_superuser(self):
        """
        Tests that we can create a admin users
        """
        email = "test@example.com"
        CaspUser.objects.create_superuser(
            username="test",
            email=email,
            password=self.password,
            first_name="Hello",
            last_name="world"
        )
        self.assertTrue(CaspUser.objects.filter(email=email).exists())
        self.assertEqual(CaspUser.objects.filter(email=email).count(), 1)
        user = CaspUser.objects.get(email=email)
        self.assertTrue(user.is_staff)
