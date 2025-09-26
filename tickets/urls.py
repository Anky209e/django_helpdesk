from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TicketViewSet, CommentViewSet, ReportView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tickets/<int:ticket_pk>/comments/', include([
        path('', CommentViewSet.as_view({'get': 'list', 'post': 'create'})),
        path('<int:pk>/', CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    ])),
    path('reports/', ReportView.as_view()),
    # Auth endpoints (using built-in, or add djoser/rest_framework_simplejwt if needed)
    # For simplicity, use DRF's default auth views or add custom login/logout.
]