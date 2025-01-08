from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    #Создаем опции для priority и status
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    title = models.CharField(max_length=70)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)  
    # так как мы указали auto_now оно будет обновлятся каждый раз при изминении обьекта и нам не нужно прописывать это во вьюхе


    def __str__(self):
        return f"{self.title} ({self.status})"
    