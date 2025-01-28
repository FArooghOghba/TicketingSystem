from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


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