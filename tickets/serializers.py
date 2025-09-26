from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket, Comment

class UserSerializer(serializers.ModelSerializer):
    nameEmail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'nameEmail']

    def get_nameEmail(self, obj):
        return f"{obj.first_name} {obj.last_name} - {obj.email}"

class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Ticket
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = '__all__'