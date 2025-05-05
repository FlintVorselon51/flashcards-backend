from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.views import APIView

from authentication.serializers import UserSerializer
from authentication.services import (
    LoginService,
    RegistrationService,
    RefreshService,
    IsEmailAvailableForRegistrationService,
    SetNewPasswordUsingCurrentService
)


User = get_user_model()

# noinspection PyMethodMayBeStatic
class Login(APIView):
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        service = LoginService(email, password)
        return service.execute()


# noinspection PyMethodMayBeStatic
class Registration(APIView):
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        service = RegistrationService(email, password)
        return service.execute()


# noinspection PyMethodMayBeStatic
class Refresh(APIView):
    authentication_classes = []

    def post(self, request):
        access_token = request.data.get('accessToken')
        refresh_token = request.data.get('refreshToken')

        service = RefreshService(access_token, refresh_token)
        return service.execute()


# noinspection PyMethodMayBeStatic
class IsEmailAvailableForRegistration(APIView):
    authentication_classes = []

    def get(self, request):
        email = request.query_params.get('email')

        service = IsEmailAvailableForRegistrationService(email)
        return service.execute()


# noinspection PyMethodMayBeStatic
class SetNewPasswordUsingCurrent(APIView):

    def post(self, request):
        user = request.user
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')

        service = SetNewPasswordUsingCurrentService(user, current_password, new_password)
        return service.execute()


class UserListView(generics.ListAPIView):
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer
