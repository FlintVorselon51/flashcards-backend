from django.contrib.auth import get_user_model
from rest_framework.response import Response

from tools.exceptions import UnprocessableEntity
from tools.services import AbstractService


User = get_user_model()


class IsEmailAvailableForRegistrationService(AbstractService):
    available: bool

    def __init__(self, email) -> None:
        self.email: str = email

    def execute(self) -> Response:
        self._check_email_is_not_empty()
        self.available = self._is_email_available_for_registration()

        return super(IsEmailAvailableForRegistrationService, self).execute()

    def _form_successful_response(self) -> Response:
        return Response({
            'email': self.email,
            'available': self.available
        })

    def _check_email_is_not_empty(self) -> None:
        if not self.email:
            raise UnprocessableEntity('Invalid request: email field is required.')

    def _is_email_available_for_registration(self) -> bool:
        try:
            User.objects.get(email=self.email)
        except User.DoesNotExist:
            return True
        return False
