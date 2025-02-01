from django.urls import path

from ticketing_system.ticket.views import (
    TicketListView, TicketCreateView, TicketDetailView,
    TicketCloseView
)


app_name = 'tickets'


urlpatterns = [
    path(route='', view=TicketListView.as_view(), name="list"),
    path(route='create/', view=TicketCreateView.as_view(), name="create"),
    path(route="<uuid:ticket_id>/", view=TicketDetailView.as_view(), name="detail"),
    path(route="<uuid:ticket_id>/close/", view=TicketCloseView.as_view(), name="close"),
]
