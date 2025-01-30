from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    """
    Custom form for creating new users.

    Inherits from Django's built-in UserCreationForm and customizes it to:
    - Require the 'email' field explicitly.
    - Remove the 'password2' field if it's not necessary.

    Meta:
        model (User): The custom user model used for authentication.
        fields (tuple): The fields to display and handle in the form.
    """

    class Meta:
        model = User
        fields = ("email", "username")  # Fields to show in registration

    def __init__(self, *args, **kwargs) -> None:

        """
        Initialize the form with custom modifications.

        - Set the 'email' field as required.
        - Remove the 'password2' field from the form.
        """

        super().__init__(*args, **kwargs)

        # Make email field required explicitly
        self.fields['email'].required = True

        # Remove password2 if not needed
        del self.fields['password2']


class CustomAuthenticationForm(AuthenticationForm):

    """
    Custom authentication form that handles email-based login.

    - Uses `email` instead of `username` as the primary login field.
    - Ensures that only verified users can log in.
    - Overrides `clean` method to handle authentication and validation.
    """

    # Not used but required by Django
    # This prevents Django from complaining about a missing username field.
    username = forms.CharField(
        required=False, widget=forms.HiddenInput()
    )

    email = forms.EmailField(
        max_length=255, required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )

    def clean(self):

        """
        Validates the provided email and password.

        - Checks if the email and password fields are filled.
        - Authenticates the user against the database.
        - Prevents unverified users from logging in.
        - Calls `confirm_login_allowed` to check if the user is active.

        Raises:
            - ValidationError if authentication fails.
            - ValidationError if the user's email is not verified.
        """

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password
            )

            # Raise error if authentication fails
            if self.user_cache is None:
                raise self.get_invalid_login_error()

            if not self.user_cache.is_verified:
                raise forms.ValidationError(
                    message="Please verify your email before logging in.",
                    code="unverified"
                )

            # Check if user is allowed to log in (e.g., is_active)
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
