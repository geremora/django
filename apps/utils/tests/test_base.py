from django.test import TestCase, Client

from ...profiles.models import CaspUser


class BaseTestCase(TestCase):
    clients = {}
    users = {}

    user = None
    username = 'jpueblo'
    email = 'jpueblo@example.com'
    password = 'abc123'

    def create_user_and_login(self):
        self.user = CaspUser.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            first_name="Dude",
            last_name="Ohio",
            phone="555-555-5555"
        )

        self.clients[self.username] = self.setup_user_client(self.username, self.password)
        self.users[self.username] = self.user

        return self.clients[self.username]

    def create_another_user_and_login(self, username='jsmith'):
        email = '{}@example.com'.format(username)
        password = 'abc123'

        user = CaspUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=username,
            last_name="Caesar"
        )

        self.clients[username] = self.setup_user_client(username, password)
        self.users[username] = user

        return self.clients[username]

    def create_superuser_and_login(self):
        self.superuser = CaspUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password=self.password,
            first_name="admin",
            last_name="admin"
        )

        self.clients["admin"] = self.setup_user_client("admin", self.password)
        self.users["admin"] = self.superuser

        return self.clients["admin"]

    def setup_user_client(self, username, password):
        client = Client()
        if client.login(username=username, password=password):
            return client
        raise Exception("Could not login with the client.")