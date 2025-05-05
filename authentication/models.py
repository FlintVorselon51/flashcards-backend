from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from authentication.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('name'), blank=True, max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
