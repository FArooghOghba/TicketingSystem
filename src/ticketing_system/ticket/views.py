from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView

from ticketing_system.ticket.models import Ticket
from ticketing_system.ticket.forms import TicketCreationForm, TicketCloseForm, TicketAssignmentForm
from ticketing_system.ticket.selectors import get_user_tickets, get_ticket_detail
from ticketing_system.ticket.services import create_ticket, close_ticket, assign_ticket
from ticketing_system.users.selectors import get_user_profile


class TicketListView(LoginRequiredMixin, ListView):

    """
    View for listing tickets based on the user's role.

    - Requires authentication (`LoginRequiredMixin`).
    - Uses pagination to display 10 tickets per page.
    - Retrieves a filtered ticket queryset via `get_user_tickets()`.
    - Adds the annotated user profile (with ticket counts) to the template context.

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
            QuerySet[Ticket]: A filtered queryset containing tickets
            relevant to the user.
        """

        user_profile = self.request.user.profile
        return get_user_tickets(user_profile=user_profile)


    def get_context_data(self, **kwargs):

        """
        Add additional context data to the template.
        Extend the context with the annotated user profile.

        - Adds `user_profile` to the context for role-based UI rendering.

        Returns:
            dict: Context data containing the user profile with aggregated
            ticket counts.
        """

        context = super().get_context_data(**kwargs)

        user = self.request.user
        context['user_profile'] = get_user_profile(user=user)
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


class TicketDetailView(LoginRequiredMixin, DetailView):

    """
    Displays the details of a specific ticket based on the user's role.

    Role-based access:
        - Admin: can view any ticket.
        - Staff: can view a ticket only if it is assigned to them.
        - Customer: can view a ticket only if they created it.

    Attributes:
        model (Ticket): The Ticket model.
        template_name (str): Template used for rendering the ticket detail.
        context_object_name (str): The variable name used for the ticket in the template.
        login_url (str): URL to redirect unauthenticated users.
    """

    model = Ticket
    template_name = "ticket/ticket_detail.html"
    context_object_name = "ticket"

    def get_object(self, queryset: Any = None) -> 'Ticket':

        """
        Retrieve the ticket object while enforcing role-based access control.

        Returns:
            Ticket: The ticket object if the user is permitted to view it.

        Raises:
            Http404: If the ticket does not exist or the user lacks permission.
        """

        user_profile = self.request.user.profile

        try:
            return get_ticket_detail(
                user_profile=user_profile, ticket_id=self.kwargs["ticket_id"]
            )
        except PermissionError:
            raise Http404("You do not have permission to view this ticket.")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:

        """
        Extend the default context with additional data.

        Adds the current user's profile and, for admin users,
        an assignment form for ticket assignment.

        Returns:
            dict: The context data to be passed to the template.
        """

        context = super().get_context_data(**kwargs)
        context["user_profile"] = self.request.user.profile

        # Add assignment form for admin users
        if self.request.user.profile.role == 'admin':
            context["assignment_form"] = TicketAssignmentForm()
        return context


class TicketAssignmentView(LoginRequiredMixin, View):

    """
    Handles ticket assignment form submission by admin users.

    This view processes a POST request to assign a ticket to a staff user.
    It validates the submitted form and, if valid, calls the service function
    to perform the assignment. If the logged-in user is not an admin, it
    immediately returns an error message.

    Attributes:
        None
    """

    def post(self, request: Any, ticket_id: str, *args: Any, **kwargs: Any) -> Any:

        """
        Process the assignment form submission.

        Args:
            request (HttpRequest): The HTTP request object.
            ticket_id (str): The unique identifier of the ticket to assign.

        Returns:
            HttpResponse: A redirection to the ticket detail page with appropriate messages.

        Raises:
            PermissionDenied: If the user does not have admin privileges.
        """

        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        form = TicketAssignmentForm(request.POST)

        if request.user.profile.role != 'admin':
            messages.error(request, message="You don't have permission to assign tickets.")
            return redirect(reverse_lazy("tickets:detail", kwargs={"ticket_id": ticket.ticket_id}))

        if form.is_valid():
            try:
                assign_ticket(
                    ticket=ticket,
                    staff_profile=form.cleaned_data["assigned_to"]
                )
                messages.success(request, message="Ticket assigned successfully.")
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, message="Invalid assignment form submission.")

        return redirect(reverse_lazy("tickets:detail", kwargs={"ticket_id": ticket.ticket_id}))


class TicketCloseView(LoginRequiredMixin, FormView):

    """
    View for closing a ticket, allowing staff or admin users to provide
    an optional closing message.

    This view presents a form for closing a ticket. Upon submission,
    it calls the `close_ticket` service function to update the ticket's status.
    Success or error messages are added accordingly, and the user is redirected
    to the ticket list.

    Attributes:
        template_name (str): Template used to render the ticket close form.
        form_class (Type[TicketCloseForm]): The form class for closing a ticket.
        success_url (str): URL to redirect to after successful form submission.
        login_url (str): URL for redirecting unauthenticated users.
    """

    template_name = "ticket/ticket_close.html"
    form_class = TicketCloseForm
    success_url = reverse_lazy("tickets:list")
    login_url = reverse_lazy("auth:login")

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:

        """
        Retrieve the ticket object based on the provided ticket_id.

        Raises:
            Http404: If the ticket is not found.

        Returns:
            HttpResponse: The result of the parent dispatch method.
        """

        # Fetch the ticket object based on ticket_id
        self.ticket = get_object_or_404(Ticket, ticket_id=self.kwargs["ticket_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: Any) -> Any:

        """
        Process the valid form submission to close the ticket.

        Retrieves the closing message from the form and attempts to close the ticket using
        the `close_ticket` service function. Appropriate success or error messages are added.

        Returns:
            HttpResponse: A redirect response to the ticket detail page.
        """

        user_profile = self.request.user.profile
        closing_message = form.cleaned_data.get("closing_message", "")

        try:
            close_ticket(user_profile=user_profile, ticket=self.ticket, closing_message=closing_message)
            messages.success(self.request, message="Ticket successfully closed.")
        except PermissionDenied:
            messages.error(self.request, message="You do not have permission to close this ticket.")
        except ValueError as e:
            messages.error(self.request, str(e))

        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:

        """
        Add the ticket to the context for rendering the form.

        Returns:
            dict: The context data, including the ticket instance.
        """

        context = super().get_context_data(**kwargs)
        context["ticket"] = self.ticket
        return context