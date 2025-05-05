import django.test
import rest_framework.test
import faker
from django.conf import settings
from django.contrib.auth import get_user_model

from booking.models import Booking

User = get_user_model()

fake = faker.Faker()


class APIClient(rest_framework.test.APIClient):

    def request(self, **kwargs):
        self.credentials(**{settings.REQUIRED_VERSION_HEADER: settings.API_VERSION})
        return super(APIClient, self).request(**kwargs)


class APITestCase(django.test.TestCase):
    client_class = APIClient


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self) -> None:
        self.email_for_user = fake.unique.email()
        self.password_for_user = fake.unique.password()

        self.user = User.objects.create_user(
            email=self.email_for_user,
            password=self.password_for_user
        )

        self.email_for_another_user = fake.unique.email()
        self.password_for_another_user = fake.unique.password()

        self.another_user = User.objects.create_user(
            email=self.email_for_another_user,
            password=self.password_for_another_user
        )

        self.client.force_authenticate(self.user)

