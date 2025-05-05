from django.contrib.auth import get_user_model, password_validation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from tools.exceptions import Conflict, UnprocessableEntity
from tools.services import AbstractService


User = get_user_model()


class RegistrationService(AbstractService):
    """With RegistrationService you can create a new user in database with the provided email and password."""

    def __init__(self, email: str | None, password: str | None) -> None:
        self.email: str | None = email
        self.password: str | None = password

    def execute(self) -> Response:
        self._check_email_and_password_not_empty()
        self._check_there_is_no_user_with_email()
        self._validate_email()
        self._validate_password()
        self._create_user()

        return super(RegistrationService, self).execute()

    def _check_email_and_password_not_empty(self) -> None:
        if not (self.email and self.password):
            raise UnprocessableEntity('Invalid request: email and password fields are required.')

    def _check_there_is_no_user_with_email(self) -> None:
        try:
            User.objects.get(email=self.email)
            raise Conflict('Provided email already in use.')
        except User.DoesNotExist:
            return

    def _validate_email(self) -> None:
        try:
            validate_email(self.email)
        except ValidationError as error:
            raise UnprocessableEntity({
                'message': 'Provided email is invalid.',
                'errors': error.error_list
            })

    def _validate_password(self) -> None:
        try:
            password_validation.validate_password(self.password)
        except ValidationError as error:
            raise UnprocessableEntity({
                'message': 'Provided password is invalid.',
                'errors': error.error_list
            })

    def _create_user(self) -> None:
        User.objects.create_user(email=self.email, password=self.password)

    def _form_successful_response(self) -> Response:
        return Response({
            'detail': 'User successfully created.'
        }, status=status.HTTP_201_CREATED)
