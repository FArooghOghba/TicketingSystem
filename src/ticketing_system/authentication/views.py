from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from ticketing_system.authentication.forms import (
    CustomUserCreationForm, CustomAuthenticationForm
)
from ticketing_system.authentication.token_service import TokenService
from ticketing_system.core.exceptions import ApplicationError
from ticketing_system.emails.services import send_registration_email
from ticketing_system.users.models import Profile


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

        try:
            # Create user with unverified status
            user = form.save()

            # Create associated profile
            Profile.objects.create(user=user)

            # Send verification email
            send_registration_email(user=user)
        except IntegrityError:
            # Handle potential duplicate profile creation
            form.add_error(None, "Profile already exists")
            return self.form_invalid(form)

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
    Custom login view that handles email-based authentication
    and verification checks.

    Features:
    - Uses `email` for authentication instead of `username`.
    - Redirects already authenticated users.
    - Ensures only verified users can log in.
    - Provides custom error messages for failed authentication.
    """

    template_name = 'authentication/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):

        """
        Returns the URL to redirect to upon successful login.

        Redirects users to the `auth:custom` page.
        """

        return reverse_lazy('tickets:list')

    def form_valid(self, form):

        """
        Handles successful login.

        - Checks if the user is verified before allowing login.
        - Displays a success message upon successful authentication.
        - Calls the parent method to complete the login process.

        Returns:
            - Redirects the user to the appropriate page.
        """

        user = form.get_user()

        if not user.is_verified:
            # Prevent login for unverified users
            messages.error(
                self.request,
                message="Account not verified. Please check your email for the verification link."
            )
            return self.form_invalid(form)

        # Only log in verified users
        messages.success(self.request, message="Logged in successfully")
        return super().form_valid(form)

    def form_invalid(self, form):

        """
        Handles unsuccessful login attempts.

        - Displays an error message for invalid credentials.
        - Calls the parent method to re-render the login form.

        Returns:
            - Renders the login form with an error message.
        """

        messages.error(self.request, message="Invalid email or password")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):

    """
    Handles user logout.

    - Logs out the authenticated user.
    - Redirects to the login page after logout.
    - Displays a success message confirming the logout.
    """

    next_page = reverse_lazy('auth:login')

    def dispatch(self, request, *args, **kwargs):

        """
        Adds a success message before logging out the user.
        """

        messages.success(request, message="You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)
