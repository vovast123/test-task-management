from django.test import TestCase

from .models import Task
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token 
from rest_framework import status

class TaskApiTestCase(TestCase):
    def setUp(self):
        #создаем юзера и админа
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin = User.objects.create_superuser(username='adminuser', password='password')
        self.client = APIClient()

        #Генерируем токены для пользователей так как у нас JWT 
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'password'})
        self.user_token = response.data['access']

        response = self.client.post('/api/token/', {'username': 'adminuser', 'password': 'password'})
        self.admin_token = response.data['access']

        #Создаем задачу для тестирования прав доступа
        self.task = Task.objects.create(
            title='Test Task1',
            description='Task description1',
            status='new',
            priority='medium',
            user=self.user 
        )

    def test_create_task_authenticated(self):
        #Пытаемся создать задачу с простого аккаунта
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        task_data = {
            'title': 'Task test',
            'description': 'Task description long',
            'status': 'new',
            'priority': 'medium',
            'user': self.user.id ,  # Передаем ID пользователя, а не объект
        }

        # Запрос на создание задачи
        response = self.client.post('/tasks/', task_data, format='json')

        # Проверка, что пользователь не может создать задачу
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_tasks_user(self):
        #Пытаемся получить списек и получить 1 обьект
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)


        #get запрос
        response = self.client.get('/tasks/',  format='json')
                
                
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        


    def test_get_tasks_id_user(self):
        #Пытаемся получить списек и получить 1 обьект
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)


        #get запрос
        response = self.client.get('/tasks/1',  format='json')
                
                
        self.assertEqual(response.status_code, status.HTTP_200_OK)