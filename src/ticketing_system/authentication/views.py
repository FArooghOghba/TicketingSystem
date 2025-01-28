from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from ticketing_system.authentication.forms import CustomUserCreationForm
from ticketing_system.emails.services import send_registration_email


User = get_user_model()


class RegistrationView(CreateView):

    """
    View to handle user registration.

    Inherits from Django's generic CreateView and uses the CustomUserCreationForm
    to register new users. Upon successful registration:
    - A new user is created with 'is_verified=False'.
    - A verification email is sent to the user.
    - Redirects to the login page.

    Attributes:
        model (User): The custom user model used for registration.
        form_class (CustomUserCreationForm): The form class for user registration.
        template_name (str): The template to render the registration page.
        success_url (str): The URL to redirect to after successful registration.
    """

    model = User
    form_class = CustomUserCreationForm
    template_name = "authentication/register.html"
    success_url = reverse_lazy("auth:login")

    def form_valid(self, form: 'CustomUserCreationForm'):

        """
        Handle valid form submissions.

        - Save the user with default 'is_verified=False' status.
        - Send a registration email to the newly created user.

        Args:
            form (CustomUserCreationForm): The validated form instance.

        Returns:
            HttpResponse: The response returned by the superclass's form_valid method.
        """

        # Create user with unverified status
        user = form.save()

        # Send verification email
        send_registration_email(user=user)

        return super().form_valid(form)


class VerifyEmailView(View):
    ...
    # def get(self, request, token):
    #     try:
    #         user = TokenService.validate_token(
    #             token,
    #             token_type='email_verify',
    #             max_age=timedelta(hours=24)
    #         )
    #         user.is_verified = True
    #         user.save()
    #         return redirect("email-verified-success")
    #     except (ApplicationError, BaseUser.DoesNotExist):
    #         return redirect("email-verification-failed")


class AccountsLoginView(LoginView):
    """
    Display the login form and handle the login action.
    """

    template_name = 'accounts/login.html'
    # form_class = CustomAuthenticationForm
    # fields = ('email', 'password')
    # redirect_authenticated_user = True
    # success_msg = 'Logged in successfully'
    # error_msg = 'Enter a correct email and password'