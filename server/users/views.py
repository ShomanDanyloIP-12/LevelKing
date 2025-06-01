from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework import status
from levels.models import Level, LevelChangeRequest


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    user = request.user
    return Response({
        'message': f'Привіт, {user.username}! Це захищена інформація.'
    })


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Користувача зареєстровано успішно."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user

    Level.objects.filter(author=user).delete()

    LevelChangeRequest.objects.filter(proposer=user).delete()

    user.delete()

    return Response({"detail": "Користувача та всі пов’язані дані видалено."}, status=status.HTTP_204_NO_CONTENT)


