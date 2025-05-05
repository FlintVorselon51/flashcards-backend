from typing import Any
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from random import getrandbits

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

TokenPayload = dict[str, Any]


class AbstractToken(ABC):

    @property
    @abstractmethod
    def lifetime(self):
        pass

    key: str

    def __init__(self, **kwargs) -> None:
        user: User = kwargs.get('user')
        key: str = kwargs.get('key')

        if user and key:
            raise ValueError('User and key cannot be set together')

        if user:
            self.user: User = user
            self.key = self._generate_token()
        elif key:
            self.key = key
        else:
            raise ValueError('User or key must be set during creation.')

    def get_user_from_token(self, **kwargs) -> User:
        token_payload: TokenPayload = self._decode_token(**kwargs)
        email = token_payload.get('email')
        return User.objects.get(email=email)

    def _generate_token(self) -> str:
        token_payload: TokenPayload = self._generate_token_payload()
        return jwt.encode(token_payload, key=settings.SECRET_KEY, algorithm=settings.TOKEN_ENCRYPTION_ALGORITHM)

    def _generate_token_payload(self) -> TokenPayload:
        return {
            'email': self.user.email,
            'exp': datetime.utcnow() + timedelta(seconds=self.lifetime),
            'jti': str(getrandbits(8))
        }

    def _decode_token(self, **kwargs) -> TokenPayload:
        return jwt.decode(
            self.key,
            key=settings.SECRET_KEY,
            algorithms=(settings.TOKEN_ENCRYPTION_ALGORITHM,),
            options=kwargs,
        )


class AccessToken(AbstractToken):
    lifetime = 600


class RefreshToken(AbstractToken):
    lifetime = 604800