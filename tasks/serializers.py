from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'created_at', 'updated_at', 'user']

        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        # Если пользователь не указал priority, устанавливаем его на 'medium'
        if 'priority' not in attrs:
            attrs['priority'] = 'medium'

        return attrs