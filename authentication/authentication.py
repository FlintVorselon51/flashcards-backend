from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from jwt import PyJWTError

from authentication.services.tokens import AccessToken


class Authentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if len(auth) == 1 or not auth or auth[0].lower() != self.keyword.lower().encode():
            msg = _('Invalid authorization header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid authorization header. Header string should not contain spaces.')
            raise AuthenticationFailed(msg)

        token = auth[1].decode()

        try:
            user = AccessToken(key=token).get_user_from_token(verify_signature=False)
            return user, token
        except PyJWTError:
            msg = _('Invalid token.')
            raise AuthenticationFailed(msg)

    def authenticate_header(self, request):
        return self.keyword
