from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, filters
from django_filters import rest_framework as django_filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Task
from .serializers import TaskSerializer
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



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
    ordering = ['-created_at']  # По умолчанию сортировать по дате создания


    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


    @method_decorator(cache_page(60 * 15))  # Кэширование для списка задач
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    


    def perform_create(self, serializer):
        super().perform_create(serializer)
        # Очистить кэш после создания задачи
        cache.delete('tasks_list')

    def perform_update(self, serializer):
        task = serializer.save()

        # Отправка обновления через WebSocket
        channel_layer = get_channel_layer()

        # Данные о задаче, которые мы отправим
        task_data = {
            'id': task.id,
            'title': task.title,
            'status': task.status,
        }
        
        # Отправляем обновление всем подключенным пользователям, следящим за задачей
        async_to_sync(channel_layer.send)(
            f'task_{task.user.id}',  # Пользователь, которому нужно отправить уведомление
            {
                'type': 'send_task_update',
                'task_data': task_data
            }
        )


        super().perform_update(serializer)
        # Очистить кэш после обновления задачи
        cache.delete('tasks_list')



    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        # Очистить кэш после удаления задачи
        cache.delete('tasks_list')