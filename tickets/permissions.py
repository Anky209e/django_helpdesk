from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='User').exists() or self.has_admin_or_agent_access(request)

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or self.has_admin_or_agent_access(request)

def has_admin_or_agent_access(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Agent']).exists()

class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Agent').exists() or request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user or request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_object_permission(self, request, view, obj):
        return True