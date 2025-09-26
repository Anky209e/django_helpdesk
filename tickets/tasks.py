from celery import shared_task
from django.core.mail import send_mail
from .models import Ticket
from django.conf import settings

@shared_task
def escalate_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.status not in ['resolved', 'closed']:
            ticket.status = 'escalated'
            ticket.save()
            # Send email alert
            send_mail(
                'Ticket Escalated',
                f'Ticket {ticket.title} has been escalated due to timeout.',
                'no-reply@helpdesk.com',
                [ticket.created_by.email, 'admin@helpdesk.com'],  # Admin email hardcoded for demo
                fail_silently=False,
            )
    except Ticket.DoesNotExist:
        pass