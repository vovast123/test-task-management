from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, filters
from django_filters import rest_framework as django_filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsTaskOwnerOrAdmin
from rest_framework.response import Response
from rest_framework import status


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Task
        fields = ['status', 'priority', 'created_at']

        
class CustomAPIListPagination(PageNumberPagination):#отдельная погинация под клас
    page_size = 20
#обычно для классов пагинации и фильтров создаются отдельные файлы filters , Pagination но так как у нас по 1 классу на каждый я решил создать их тут



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all() #достаем все задачи
    serializer_class = TaskSerializer 
    pagination_class = CustomAPIListPagination

    # Фильтрация по полям: статусу, приоритету и дате созданиям
    filter_backends = (filters.OrderingFilter, django_filters.DjangoFilterBackend)
    filterset_class = TaskFilter

    # Сортировка задач по дате создания
    ordering_fields = ['created_at']
    ordering = ['created_at']  # По умолчанию сортировать по дате создания


    authentication_classes = [JWTAuthentication]


    permission_classes = [permissions.IsAuthenticated, IsTaskOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        ''' Я провел тесты и к сожелению даже если в permission написать 
            if request.method == 'POST': и запретить ,то не блокирует так как 
            has_object_permission вызывается только при доступе к существующему объекту  '''
        
        if not request.user.is_staff:  
            return Response(
                {'detail': 'You do not have permission to create tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
