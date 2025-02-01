from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView

from ticketing_system.ticket.models import Ticket
from ticketing_system.ticket.forms import TicketCreationForm, TicketCloseForm
from ticketing_system.ticket.selectors import get_user_tickets, get_ticket_detail
from ticketing_system.ticket.services import create_ticket, close_ticket


class TicketListView(LoginRequiredMixin, ListView):

    """
    View for listing tickets based on the user's role.

    - Requires authentication (`LoginRequiredMixin`).
    - Uses pagination to display 10 tickets per page.
    - Calls `get_user_tickets()` to retrieve the correct ticket queryset.
    - Adds the `user_profile` to the context for template access.

    Attributes:
        model (Ticket): The model associated with this view.
        login_url (str): Redirect URL for unauthenticated users.
        template_name (str): Template used to render the ticket list.
        context_object_name (str): Name of the queryset in the template.
        paginate_by (int): Number of tickets per page.
    """

    model = Ticket
    login_url = reverse_lazy('auth:login')
    template_name = 'ticket/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):

        """
        Get the ticket queryset based on the user's profile.

        Returns:
            QuerySet[Ticket]: A filtered queryset containing tickets relevant to the user.
        """

        user_profile = self.request.user.profile
        return get_user_tickets(user_profile=user_profile)


    def get_context_data(self, **kwargs):

        """
        Add additional context data to the template.

        - Adds `user_profile` to the context for role-based UI rendering.

        Returns:
            dict: The context data for rendering the template.
        """

        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user.profile
        return context


class TicketCreateView(LoginRequiredMixin, CreateView):

    model = Ticket
    form_class = TicketCreationForm
    template_name = "ticket/ticket_create.html"
    success_url = reverse_lazy("tickets:list")

    def form_valid(self, form):

        """Overrides form_valid to use the service function."""

        create_ticket(
            created_by=self.request.user.profile,
            subject=form.cleaned_data["subject"],
            description=form.cleaned_data["description"],
            file=form.cleaned_data.get("file"),
        )
        return redirect(self.success_url)


