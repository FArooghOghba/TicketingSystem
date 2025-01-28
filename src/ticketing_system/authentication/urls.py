from django.contrib.auth.views import LoginView
from django.urls import path

from ticketing_system.authentication.views import (
    RegistrationView, VerifyEmailView,
)


app = 'auth'


urlpatterns = [
    path(route="register/", view=RegistrationView.as_view(), name="register"),
    path(route="verify-email/<str:token>/", view=VerifyEmailView.as_view(), name="verify-email"),
    path(route="login/", view=LoginView.as_view(), name="login"),
    # path(rout="logout/", LogoutView.as_view(next_page="home"), name="logout"),
]
