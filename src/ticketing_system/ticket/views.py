from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from ticketing_system.ticket.models import Ticket
from ticketing_system.ticket.services import get_user_tickets


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