from django.urls import path

from ticketing_system.ticket.views import (
    TicketListView,
)


app_name = 'tickets'


urlpatterns = [
    path(route='', view=TicketListView.as_view(), name="list"),
]
