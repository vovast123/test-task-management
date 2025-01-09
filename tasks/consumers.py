import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем идентификатор текущего пользователя
        self.user = self.scope['user']

        # Генерируем уникальный канал для каждого пользователя
        self.room_name = f'task_{self.user.id}'


        # Разрешаем соединение
        await self.accept()

    # Метод, который будет отправлять обновления в WebSocket
    async def send_task_update(self, event):
        # Получаем данные для отправки
        task_data = event['task_data']

        # Отправляем данные в WebSocket
        await self.send(text_data=json.dumps({
            'message': f"Задача '{task_data['title']}' обновлена. Новый статус: {task_data['status']}",
            'task_data': task_data  
        }))




