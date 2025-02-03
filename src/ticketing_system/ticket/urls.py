from django.urls import path

from ticketing_system.ticket.views import (
    TicketListView, TicketCreateView, TicketDetailView,
    TicketCloseView, TicketAssignmentView
)


app_name = 'tickets'


urlpatterns = [
    path(route='', view=TicketListView.as_view(), name="list"),
    path(route='create/', view=TicketCreateView.as_view(), name="create"),
    path(route="<uuid:ticket_id>/", view=TicketDetailView.as_view(), name="detail"),
    path(route="<uuid:ticket_id>/assign/", view=TicketAssignmentView.as_view(), name="assign"),
    path(route="<uuid:ticket_id>/close/", view=TicketCloseView.as_view(), name="close"),
]
