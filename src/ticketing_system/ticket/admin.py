from django.contrib import admin

from ticketing_system.ticket.models import Ticket


# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    """

    """

    list_display = [
        'created_by',
        'assigned_to',
        'subject',
        'status',
        'priority',
    ]