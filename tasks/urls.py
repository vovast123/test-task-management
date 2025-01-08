from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Получаем токен
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновляем токен
    path('', include(router.urls)), 
    
]