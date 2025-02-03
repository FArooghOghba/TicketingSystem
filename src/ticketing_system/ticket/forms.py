from django import forms

from ticketing_system.ticket.models import Ticket
from ticketing_system.users.models import Profile


class TicketCreationForm(forms.ModelForm):
    """Form for creating a new support ticket."""

    class Meta:
        model = Ticket
        fields = ["subject", "description", "file"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter subject"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe your issue"
                }
            ),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class TicketAssignmentForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        queryset=Profile.objects.filter(role='staff').order_by('user__username'),
        label="Assign to Staff",
        required=True
    )


class TicketCloseForm(forms.Form):
    """
    Form for closing a ticket with an optional closing message.
    """
    closing_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a closing message (optional)...',
            'rows': 4,
        }),
        help_text="Optionally provide details about the resolution."
    )
