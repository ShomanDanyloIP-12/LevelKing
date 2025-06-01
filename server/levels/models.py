from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Level(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='levels')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class LevelChangeRequest(models.Model):
    original_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='change_requests')
    proposer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposed_changes')
    proposed_data = models.JSONField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"Зміна до '{self.original_level.title}' від {self.proposer.username} ({self.status})"
