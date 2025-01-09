import os
import jwt

from django.core.asgi import get_asgi_application
from django.conf import settings
from django.contrib.auth import get_user_model


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from tasks.consumers import TaskStatusConsumer 
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async


User = get_user_model()
#Middleware для роботы весокета с JWT
class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def connect(self):
        # Извлекаем токен из WebSocket
        token = self.scope.get('headers', {}).get('Authorization', None)

        if token is None:
            await self.close()
            return

        # Извлекаем токен
        token = token.decode().split(' ')[1]
        
        try:
            # Декодируем JWT
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = await self.get_user(payload['user_id'])
            self.scope['user'] = user  
        except jwt.ExpiredSignatureError:
            await self.close()  
            return
        except jwt.DecodeError:
            await self.close() 
            return

        await super().connect()

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_management.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": 
    JWTAuthMiddleware(
        AuthMiddlewareStack(  
            URLRouter({
                # Указываем URL 
                'ws/tasks/': TaskStatusConsumer.as_asgi(),
            })
        )
    ),
})
