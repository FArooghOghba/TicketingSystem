from django.contrib.auth.views import LoginView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from ticketing_system.authentication.forms import CustomUserCreationForm
from ticketing_system.authentication.token_service import TokenService
from ticketing_system.core.exceptions import ApplicationError
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
    success_url = reverse_lazy("auth:verification-send")

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


class ActivationSendView(TemplateView):

     """
    View to render the activation email sent confirmation page.

    This view displays a message informing the user that a verification email
    has been sent to their registered email address.
    """

    template_name = 'authentication/verification-send.html'


class VerificationEmailView(TemplateView):

    """
    View to handle email verification via JWT tokens.

    This view verifies the token provided in the URL, checks if the user's account
    is already verified, and updates the user's verification status if necessary.

    If the token is valid and the user is unverified, their account is marked as verified.
    If the token is invalid or expired, an error message is displayed.

    Attributes:
        template_name (str): The path to the template used to display verification results.
    """

    template_name = 'authentication/verification-result.html'

    def get(self, request, *args, **kwargs):

        """
        Handle GET requests for email verification.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments, including the JWT token.

        Returns:
            HttpResponse: Renders a template with verification status and messages.

        Context Variables:
            status (str): The verification result ('success', 'already_verified', or 'error').
            message (str): The corresponding message for the verification status.
        """

        context = {}
        token = kwargs.get('token')

        try:
            user = TokenService.validate_token(
                token=token,
                max_age=settings.DEFAULT_REGISTRATION_EMAIL_JWT_MAX_AGE
            )

            if user.is_verified:
                context['status'] = 'already_verified'
                context['message'] = 'Your account has already been verified.'
            else:
                user.is_verified = True
                user.save()
                context['status'] = 'success'
                context['message'] = 'Account verified successfully!'

        except ApplicationError as e:
            context['status'] = 'error'
            context['message'] = str(e)
        except User.DoesNotExist:
            context['status'] = 'error'
            context['message'] = 'User account not found'

        return self.render_to_response(context)


class CustomLoginView(LoginView):
    """
    Display the login form and handle the login action.
    """

    template_name = 'authentication/login.html'
#     # form_class = CustomAuthenticationForm
#     # fields = ('email', 'password')
#     # redirect_authenticated_user = True
#     # success_msg = 'Logged in successfully'
#     # error_msg = 'Enter a correct email and password'