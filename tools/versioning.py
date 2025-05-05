from django.conf import settings
from rest_framework.versioning import BaseVersioning

from tools.exceptions import PreconditionFailed


class XAPIVersionScheme(BaseVersioning):
    def determine_version(self, request, *args, **kwargs):
        version = request.META.get(settings.REQUIRED_VERSION_HEADER)
        if version:
            if version == settings.API_VERSION:
                return version
            msg = f'The unsupportable API {version} version detected. Supported API version is {settings.API_VERSION}.'
            raise PreconditionFailed(msg)
        raise PreconditionFailed(f'Header "{settings.REQUIRED_VERSION_HEADER}" is not defined.')
