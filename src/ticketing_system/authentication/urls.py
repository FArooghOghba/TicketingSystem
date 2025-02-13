from django.urls import path

from ticketing_system.authentication.views import (
    RegistrationView, ActivationSendView, VerificationEmailView,
    CustomLoginView, CustomLogoutView
)


app = 'auth'


urlpatterns = [
    path(route="register/", view=RegistrationView.as_view(), name="register"),
    path(route="verification-send/", view=ActivationSendView.as_view(), name="verification-send"),
    path(route="verify-email/<str:token>/", view=VerificationEmailView.as_view(), name="verify-email"),
    path(route="", view=CustomLoginView.as_view(), name="login"),
    path(route="logout/", view=CustomLogoutView.as_view(), name="logout"),
]
