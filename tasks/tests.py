from django.test import TestCase
from .models import Task

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache



class TaskApiTestCase(TestCase):
    # Настройка перед тестами
    def setUp(self):
        #создаем юзера и админа
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()

        #Генерируем токены для пользователей так как у нас JWT 
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'password'})
        self.user_token = response.data['access']


        #Создаем задачу для тестирования прав доступа
        self.task = Task.objects.create(
            title='Test Task1',
            description='Task description1',
            status='new',
            priority='medium',
            user=self.user 
        )

    # GET запросы
    def test_get_unauthorized(self):
        #Пытаемся получить список когда не авторизован


        #GET запрос
        response = self.client.get('/tasks/',  format='json')
                
                
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    def test_get_tasks_user(self):
        #Пытаемся получить список 
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)


        #GET запрос
        response = self.client.get('/tasks/',  format='json')
                
                
        self.assertEqual(response.status_code, status.HTTP_200_OK)



    def test_get_tasks_id_user(self):
        #Пытаемся получить 1 обьект
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        
        #GET запрос
        response = self.client.get(f'/tasks/{self.task.id}/',  format='json')
        
                
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_filter_and_pagination(self):

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        # Создаем дополнительные задачи для проверки пагинации
        Task.objects.create(title='Test Task2', description='Task description2', status='new', priority='low', user=self.user)
        Task.objects.create(title='Test Task3', description='Task description3', status='new', priority='high', user=self.user)

        # GET запрос с фильтром по имени и проверкой первой страницы
        response = self.client.get('/tasks/?title=Test Task1&page=1', format='json')
        
        
        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что задачи на странице соответствуют фильтру
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Task1')
        


    def test_get_noexistent_page(self):
    
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        # GET запрос для несуществующей страницы
        response = self.client.get('/tasks/?page=5', format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



    # POST Запрос 
    def test_post_task_authenticated(self):
        #Пытаемся создать задачу 
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        task_data = {
            'title': 'Task test',
            'description': 'Task description long',
            'status': 'new',
            'priority': 'medium',
            'user': self.user.id , 
        }

        response = self.client.post('/tasks/', task_data, format='json')

        # Проверка, что пользователь не может создать задачу
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    #PATCH Запрос
    def test_patch_user_status(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        task_data = {
            'status': 'in_progress',
        }

        response = self.client.patch(f'/tasks/{self.task.id}/', task_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #PUT Запрос
    def test_put_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        task_data = {
            'title': 'Task test2',
            'description': 'Task description long so',
            'status': 'in_progress',
            'priority': 'medium',
            'user': self.user.id , 
        }

        #PATCH Запрос
        response = self.client.put(f'/tasks/{self.task.id}/', task_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #DELETE запрос
    def test_delete_task(self):
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        response = self.client.delete(f'/tasks/{self.task.id}/', format='json')

        # Проверяем, что запрос успешен
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что задача  удалена
        response = self.client.get(f'/tasks/{self.task.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    #Тест на роботу кеша
    def test_cache(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)

        cache.set('tasks_list', 'cached_data', timeout=60 * 15)

        # Проверяем, что данные кэшируются
        response = self.client.get('/tasks/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что список задач был закэширован
        cached_tasks = cache.get('tasks_list')
        print("Cached Tasks:", cached_tasks)
        self.assertIsNotNone(cached_tasks) 

        #Обновляем задачу
        updated_task_data = {'title': 'Updated Task'}
        self.client.patch(f'/tasks/{self.task.id}/', updated_task_data, format='json')
        
        
        cached_tasks_after_update = cache.get('tasks_list')
        print("Cached Tasks After Update:", cached_tasks_after_update)
        self.assertIsNone(cached_tasks_after_update) # Кэш должен быть очищен



