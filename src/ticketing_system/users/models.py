from typing import Optional, Union

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ticketing_system.core.models import BaseModel
from ticketing_system.ticket.models import Ticket, TicketStatus


class CustomUserManager(BaseUserManager['BaseUser']):

    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
            self, email: str, username: str, password: Optional[str] = None,
            **extra_fields: Union[str, bool]
    ) -> 'BaseUser':

        """
        Creates and saves a User with the given email, username, and password.

        :param email: (str): The email address of the user.
        :param username: (str): The username of the user.
        :param password: (str, optional): The password of the user. Defaults to None.
        :param extra_fields: (str): Additional fields to save on the user.

        :return: User: The newly created user.

        :raises: ValueError: If the email or username is not provided.
        """

        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError('The username must be set.')

        user = self.model(
            email=self.normalize_email(email.lower()),
            username=username,
            **extra_fields
        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(
            self, email: str, username: str, password: Optional[str] = None,
            **extra_fields: Union[str, bool]
    ) -> 'BaseUser':

        """
        Creates and saves a superuser with the given email and password.

        :param: email (str): The email address of the superuser.
        :param: username (str): The username of the superuser.
        :param: password (str, optional): The password of the superuser.
                        Defaults to None.
        :param: extra_fields: Additional fields to save on the superuser.

        :returns: User: The newly created superuser.

        :raises: ValueError: If the is_staff or is_superuser fields
                            are not set to True.
        """

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )

        user.save(using=self._db)

        return user


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):

    """
    Custom User Model Based on AbstractBaseUser & PermissionMixin for
    creating a custom user model and adding email as USERNAME FIELD.
    """

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(_("email address"), max_length=150, unique=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        }
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    is_verified = models.BooleanField(
        _("verified"),
        default=False,
        help_text=_(
            "Designates whether this user verified his account. "
        ),
    )

    is_superuser = models.BooleanField(
        _('superuser'),
        default=False,
        help_text=_(
            "Designates whether this user is super user."
        ),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return self.email


class UserRole(models.TextChoices):

    """
    Enum for user roles in the ticketing system.
    """

    CUSTOMER = "customer", _("Customer")
    STAFF = "staff", _("Staff")
    ADMIN = "admin", _("Admin")


class Profile(BaseModel):

    """
    Profile model for a user in the ticketing system.

    This model provides computed properties to dynamically count
    the tickets created or assigned to the user without storing manual
    counters.
    """

    user = models.OneToOneField(
        to=BaseUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
        help_text=_("The user associated with this profile."),
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        verbose_name=_("Role"),
        help_text=_("Role of the user in the ticketing system."),
    )

    @property
    def created_ticket_count(self) -> int:

        """
        Returns the total number of tickets created by this profile.
        """

        return Ticket.objects.filter(created_by=self).count()

    @property
    def assigned_ticket_count(self) -> int:

        """
        Returns the total number of tickets assigned to this profile.
        """

        return Ticket.objects.filter(assigned_to=self).count()

    @property
    def pending_ticket_count(self) -> int:

        """
        Returns the number of pending tickets created by this profile.
        """

        return Ticket.objects.filter(created_by=self, status=TicketStatus.PENDING).count()

    @property
    def in_progress_ticket_count(self) -> int:

        """
        Returns the number of tickets in progress created by this profile.
        """

        return Ticket.objects.filter(created_by=self, status=TicketStatus.IN_PROGRESS).count()

    @property
    def closed_ticket_count(self) -> int:

        """
        Returns the number of closed tickets created by this profile.
        """

        return Ticket.objects.filter(created_by=self, status=TicketStatus.CLOSED).count()

    def __str__(self):

        return f"Profile of {self.user.email} with Role {self.get_role_display()}"
