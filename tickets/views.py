from rest_framework import viewsets, generics, permissions, filters
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import Ticket, Comment
from .serializers import TicketSerializer, CommentSerializer, UserSerializer
from .permissions import IsUser, IsAgent, IsAdmin
from .tasks import escalate_ticket

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]  # Admins only for full access
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    @extend_schema(
        description='Search users by keyword, returns with computed nameEmail field.',
        parameters=[
            OpenApiParameter(name='search', description='Keyword search', required=False, type=str),
        ],
        examples=[
            OpenApiExample('Example', value={'id': 1, 'nameEmail': 'John Doe - john@example.com'}),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['create', 'list']:  # Allow registration without admin
            return [permissions.AllowAny()]
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]  # Users can edit/delete own account
        return super().get_permissions()

    def get_object(self):
        obj = super().get_object()
        if self.request.user == obj or self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists():
            return obj
        self.permission_denied(self.request)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['title', 'status', 'priority', 'assigned_to']
    search_fields = ['title']

    def get_permissions(self):
        if self.action == 'create':
            return [IsUser()]
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update']:
            return [IsAgent()]
        if self.action in ['destroy']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            return Ticket.objects.all()
        elif user.groups.filter(name='Agent').exists():
            return Ticket.objects.filter(assigned_to=user)
        else:
            return Ticket.objects.filter(created_by=user)

    def perform_create(self, serializer):
        ticket = serializer.save(created_by=self.request.user)
        # Schedule escalation
        delay = self.request.settings.ESCALATION_TIMEFRAMES.get(ticket.priority, timedelta(hours=24))
        escalate_ticket.apply_async((ticket.id,), eta=timezone.now() + delay)

    @extend_schema(
        description='API to search/filter tickets by title, status, priority, assigned_to.',
        parameters=[
            OpenApiParameter(name='title', description='Ticket title', required=False, type=str),
            OpenApiParameter(name='status', description='Ticket status', required=False, type=str),
            OpenApiParameter(name='priority', description='Ticket priority', required=False, type=str),
            OpenApiParameter(name='assigned_to', description='Assigned user ID', required=False, type=int),
        ],
        examples=[
            OpenApiExample('Filtered List', value=[{'id': 1, 'title': 'Issue', 'status': 'open'}]),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAgent()]  # Agents add comments
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Comment.objects.filter(ticket__id=self.kwargs['ticket_pk'])

    def perform_create(self, serializer):
        ticket = Ticket.objects.get(id=self.kwargs['ticket_pk'])
        serializer.save(user=self.request.user, ticket=ticket)

class ReportView(generics.GenericAPIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        description='Reporting endpoint: Number of tickets opened, resolved, escalated in last 7 days.',
        responses={200: OpenApiExample('Stats', value={'opened': 5, 'resolved': 3, 'escalated': 1})}
    )
    def get(self, request):
        last_week = timezone.now() - timedelta(days=7)
        opened = Ticket.objects.filter(created_at__gte=last_week).count()
        resolved = Ticket.objects.filter(status='resolved', updated_at__gte=last_week).count()
        escalated = Ticket.objects.filter(status='escalated', updated_at__gte=last_week).count()
        return Response({'opened': opened, 'resolved': resolved, 'escalated': escalated})