from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, filters
from django_filters import rest_framework as django_filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Task
from .serializers import TaskSerializer
from rest_framework.response import Response
from rest_framework import status


class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter()
    status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Task
        fields = ['title','status', 'priority', 'created_at']

        
class CustomAPIListPagination(PageNumberPagination):#отдельная погинация под клас
    page_size = 20
#обычно для классов пагинации и фильтров создаются отдельные файлы filters , Pagination но так как у нас по 1 классу на каждый я решил создать их тут



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all() #достаем все задачи
    serializer_class = TaskSerializer 
    pagination_class = CustomAPIListPagination

    # Фильтрация 
    filter_backends = (filters.OrderingFilter, django_filters.DjangoFilterBackend)
    filterset_class = TaskFilter

    # Сортировка задач по дате создания
    ordering_fields = ['created_at']
    ordering = ['created_at']  # По умолчанию сортировать по дате создания


    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
