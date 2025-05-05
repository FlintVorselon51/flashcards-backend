from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from rest_framework.response import Response

from tools.exceptions import UnprocessableEntity
from tools.services import AbstractService


User = get_user_model()


class SetNewPasswordUsingCurrentService(AbstractService):
    user: User
    current_password: str
    new_password: str

    def __init__(self, user: User, current_password: str, new_password: str) -> None:
        self.user = user
        self.current_password = current_password
        self.new_password = new_password

    def execute(self) -> Response:
        self._check_passwords_not_empty()
        self._check_current_password()
        self._validate_new_password()
        self._set_new_password()

        return super(SetNewPasswordUsingCurrentService, self).execute()

    def _form_successful_response(self) -> Response:
        return Response({
            'detail': 'Password successfully changed.'
        })

    def _check_passwords_not_empty(self) -> None:
        if not (self.current_password and self.new_password):
            raise UnprocessableEntity('Invalid request: currentPassword and newPassword fields are required.')

    def _check_current_password(self) -> None:
        if not self.user.check_password(self.current_password):
            raise UnprocessableEntity('Wrong currentPassword.')

    def _validate_new_password(self) -> None:
        try:
            password_validation.validate_password(self.new_password)
        except ValidationError as error:
            raise UnprocessableEntity({
                'message': 'Provided newPassword is invalid.',
                'errors': error.error_list
            })

    def _set_new_password(self) -> None:
        self.user.set_password(self.new_password)
        self.user.save()
