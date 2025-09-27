# Helpdesk & Ticket Management System

This is a Django-based backend API for a Helpdesk system using DRF, Celery for escalations, and drf-spectacular for docs.

## Setup
1. Clone the repo.
2. `pip install -r requirements.txt`
3. `python manage.py makemigrations`
4. `python manage.py migrate`
5. Create groups in shell: Group.objects.get_or_create(name='User/Agent/Admin')
6. `python manage.py createsuperuser` for admin.
7. `python manage.py runserver`
8. Celery: `celery -A helpdesk worker -l info`

## Endpoints
- Auth: /api/auth/register/, /api/auth/login/, etc.
- Tickets: /api/tickets/ (list/create), /api/tickets/{id}/ (detail/update/delete)
- Comments: /api/comments/ (for bonus)
- Search tickets: /api/tickets/?title=...&status=...&priority=...&assigned_to=...
- Search users: /api/users/?search=... (with nameEmail field)
- Reports: /api/reports/ (bonus: tickets stats last 7 days)

Docs: /api/schema/swagger-ui/

## Celery Setup
Uses Redis as broker. Set CELERY_BROKER_URL in settings.py if needed.
Escalations are delayed tasks triggered on ticket creation.