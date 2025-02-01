from django import forms

from ticketing_system.ticket.models import Ticket


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

