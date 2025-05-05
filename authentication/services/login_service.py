from django.contrib.auth import get_user_model
from rest_framework.response import Response

from tools.exceptions import UnprocessableEntity
from tools.services import AbstractService
from authentication.services.tokens import AccessToken, RefreshToken


User = get_user_model()


class LoginService(AbstractService):
    user: User
    access_token: AccessToken
    refresh_token: RefreshToken

    def __init__(self, email: str | None, password: str | None):
        self.email: str | None = email
        self.password: str | None = password

    def execute(self) -> Response:
        self._check_email_and_password_not_empty()
        self.user = self._find_user_with_email()
        self._check_password()
        self.access_token = self._generate_access_token()
        self.refresh_token = self._generate_refresh_token()

        return super(LoginService, self).execute()

    def _form_successful_response(self):
        return Response({
            'name': self.user.name,
            'accessToken': self.access_token.key,
            'refreshToken': self.refresh_token.key
        })

    def _check_email_and_password_not_empty(self) -> None:
        if not (self.email and self.password):
            raise UnprocessableEntity('Invalid request: email and password fields are required.')

    def _find_user_with_email(self) -> User:
        try:
            return User.objects.get(email=self.email)
        except User.DoesNotExist:
            raise UnprocessableEntity('User with provided email not found.')

    def _check_password(self):
        if not self.user.check_password(self.password):
            raise UnprocessableEntity('Wrong password.')

    def _generate_access_token(self) -> AccessToken:
        return AccessToken(user=self.user)

    def _generate_refresh_token(self) -> RefreshToken:
        return RefreshToken(user=self.user)
