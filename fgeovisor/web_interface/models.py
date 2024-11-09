import uuid
from django.contrib.gis.db import models
from django.contrib.auth.models import User

# Временное хранилище данных сессии пользователя
class SessionStorage(models.Model):
    login = models.ForeignKey(User, on_delete=models.CASCADE)
    # Хранение временных данных сессии (например, черновики)
    data = models.JSONField()
    expires_at = models.DateTimeField()  # Время истечения сессии

    def __str__(self):
        return f"Сессия для {self.login} истекает в {self.expires_at}"


# Модель для отслеживания активности пользователей
class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('created_polygon', 'Created Polygon'),
        ('updated_polygon', 'Updated Polygon'),
        ('deleted_polygon', 'Deleted Polygon'),
        ('uploaded_image', 'Uploaded Image'),
        ('deleted_image', 'Deleted Image'),
    )
    login = models.ForeignKey(User, on_delete=models.CASCADE, 
                                related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    # Дополнительная информация о действии в формате JSON
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.login.username} - {self.action} в {self.created_at}"