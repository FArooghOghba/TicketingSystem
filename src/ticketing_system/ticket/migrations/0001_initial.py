# Generated by Django 4.2.18 on 2025-01-31 10:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ticket_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Unique identifier for this ticket.', unique=True, verbose_name='Ticket ID')),
                ('subject', models.CharField(help_text='Short summary of the issue.', max_length=255, verbose_name='Subject')),
                ('description', models.TextField(help_text='Detailed description of the issue.', verbose_name='Description')),
                ('file', models.FileField(blank=True, help_text='Optional file attachment.', null=True, upload_to='tickets/files/', verbose_name='Attachment')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('closed', 'Closed')], db_index=True, default='pending', help_text='Current status of the ticket.', max_length=15, verbose_name='Status')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], db_index=True, default='medium', help_text='Priority level of the ticket.', max_length=10, verbose_name='Priority')),
                ('assigned_to', models.ForeignKey(blank=True, help_text='The support agent handling the ticket.', limit_choices_to={'role': 'staff'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to='users.profile', verbose_name='Assigned To')),
                ('created_by', models.ForeignKey(help_text='Profile who created the ticket.', on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='users.profile', verbose_name='Profile')),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
                'ordering': ['-updated_at', '-created_at'],
            },
        ),
    ]
