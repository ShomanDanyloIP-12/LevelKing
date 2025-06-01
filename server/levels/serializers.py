from rest_framework import serializers
from .models import Level

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'author', 'title', 'description', 'data', 'created_at', 'is_public']
        read_only_fields = ['id', 'author', 'created_at']