from django.urls import path

from authentication.views import (
    Login,
    Registration,
    Refresh,
    IsEmailAvailableForRegistration,
    SetNewPasswordUsingCurrent, UserListView,
)


app_name = 'authentication'

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('register/', Registration.as_view(), name='register'),
    path('refresh/', Refresh.as_view(), name='refresh'),
    path(
        'is-email-available-for-registration/',
        IsEmailAvailableForRegistration.as_view(),
        name='is-email-available-for-registration'
    ),
    path(
        'set-new-password-using-current/',
        SetNewPasswordUsingCurrent.as_view(),
        name='set-new-password-using-current'
    ),
    path('users/', UserListView.as_view(), name='user-list'),
]
