from django.contrib.auth import get_user_model
from rest_framework.response import Response
from jwt import PyJWTError

from tools.exceptions import UnprocessableEntity
from tools.services import AbstractService
from authentication.services.tokens import AccessToken, RefreshToken


User = get_user_model()


class RefreshService(AbstractService):
    user: User
    access_token_user: User
    refresh_token_user: User

    access_token: AccessToken
    refresh_token: RefreshToken

    def __init__(self, access_token: str, refresh_token: str) -> None:
        self.access_token_key: str = access_token
        self.refresh_token_key: str = refresh_token

    def execute(self) -> Response:
        self._check_access_token_and_refresh_token_not_empty()
        self.access_token_user = self._get_user_from_access_token()
        self.refresh_token_user = self._get_user_from_refresh_token()
        self._check_access_token_user_and_refresh_token_user_are_same()
        self.access_token = self._generate_access_token()
        self.refresh_token = self._generate_refresh_token()

        return super(RefreshService, self).execute()

    def _form_successful_response(self) -> Response:
        return Response({
            'name': self.user.name,
            'accessToken': self.access_token.key,
            'refreshToken': self.refresh_token.key
        })

    def _check_access_token_and_refresh_token_not_empty(self):
        if not (self.access_token_key and self.refresh_token_key):
            raise UnprocessableEntity('Invalid request: accessToken and refreshToken fields are required.')

    def _get_user_from_access_token(self) -> User:
        access_token: AccessToken = AccessToken(key=self.access_token_key)
        try:
            return access_token.get_user_from_token(verify_exp=False)
        except PyJWTError:
            raise UnprocessableEntity('Provided accessToken is invalid.')

    def _get_user_from_refresh_token(self) -> User:
        refresh_token: RefreshToken = RefreshToken(key=self.refresh_token_key)
        try:
            return refresh_token.get_user_from_token(key=self.refresh_token_key)
        except PyJWTError:
            raise UnprocessableEntity('Provided refreshToken is invalid.')

    def _check_access_token_user_and_refresh_token_user_are_same(self) -> None:
        if self.access_token_user != self.refresh_token_user:
            raise UnprocessableEntity('Provided tokens are invalid.')
        self.user = self.access_token_user

    def _generate_access_token(self) -> AccessToken:
        return AccessToken(user=self.user)

    def _generate_refresh_token(self) -> RefreshToken:
        return RefreshToken(user=self.user)
