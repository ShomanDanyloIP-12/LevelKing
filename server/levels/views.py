from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import Level, LevelChangeRequest
from .serializers import LevelSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_level(request):
    serializer = LevelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_levels(request):
    levels = Level.objects.filter(is_public=True)
    serializer = LevelSerializer(levels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_levels_by_author(request, username):
    levels = Level.objects.filter(is_public=True, author__username=username)
    serializer = LevelSerializer(levels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_level_by_id(request, level_id):
    try:
        level = Level.objects.get(id=level_id)
        return Response({
            'id': level.id,
            'title': level.title,
            'description': level.description,
            'data': level.data,
            'is_public': level.is_public,
            'author': level.author.username,
        })
    except Level.DoesNotExist:
        return Response({'detail': 'Рівень не знайдено.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def propose_change(request, level_id):
    try:
        original = Level.objects.get(id=level_id)
    except Level.DoesNotExist:
        return Response({'detail': 'Рівень не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

    if original.author == request.user:
        return Response({'detail': 'Ви не можете пропонувати зміни до власного рівня.'}, status=status.HTTP_400_BAD_REQUEST)

    proposed_data = request.data.get('data')
    comment = request.data.get('comment', '')

    if not proposed_data:
        return Response({'detail': 'Поле "data" є обовʼязковим.'}, status=status.HTTP_400_BAD_REQUEST)

    LevelChangeRequest.objects.create(
        original_level=original,
        proposer=request.user,
        proposed_data=proposed_data,
        comment=comment
    )

    return Response({'detail': 'Зміни успішно запропоновано.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_change_requests(request):
    user = request.user
    # Знаходимо всі рівні, автором яких є поточний користувач
    user_levels = Level.objects.filter(author=user)

    # Отримуємо всі запити на зміну до цих рівнів
    changes = LevelChangeRequest.objects.filter(original_level__in=user_levels)

    result = [{
        'id': change.id,
        'level_id': change.original_level.id,
        'level_title': change.original_level.title,
        'proposed_data': change.proposed_data,
        'status': change.status,
        'comment': change.comment,
        'proposer': change.proposer.username,
        'created_at': change.created_at
    } for change in changes]

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_change_request_by_id(request, change_id):
    try:
        change = LevelChangeRequest.objects.get(id=change_id)
    except LevelChangeRequest.DoesNotExist:
        return Response({'detail': 'Запит на зміну не знайдено.'}, status=404)

    # Автор рівня або той, хто створив пропозицію, має бачити
    if change.original_level.author != request.user and change.proposer != request.user:
        return Response({'detail': 'У вас немає прав на перегляд цього запиту.'}, status=403)

    result = {
        'id': change.id,
        'level_id': change.original_level.id,
        'level_title': change.original_level.title,
        'proposed_data': change.proposed_data,
        'status': change.status,
        'comment': change.comment,
        'proposer': change.proposer.username,
        'created_at': change.created_at
    }

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_change(request, level_id, change_id):
    try:
        level = Level.objects.get(id=level_id)
        change = LevelChangeRequest.objects.get(id=change_id, original_level=level)
    except (Level.DoesNotExist, LevelChangeRequest.DoesNotExist):
        return Response({'detail': 'Рівень або запит не знайдено.'}, status=404)

    if level.author != request.user:
        return Response({'detail': 'Ви не маєте прав на зміну цього рівня.'}, status=403)

    level.data = change.proposed_data
    level.save()

    change.status = 'accepted'
    change.save()

    return Response({'detail': 'Зміни прийнято та застосовано.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_change(request, level_id, change_id):
    try:
        level = Level.objects.get(id=level_id)
        change = LevelChangeRequest.objects.get(id=change_id, original_level=level)
    except (Level.DoesNotExist, LevelChangeRequest.DoesNotExist):
        return Response({'detail': 'Рівень або запит не знайдено.'}, status=404)

    if level.author != request.user:
        return Response({'detail': 'Ви не маєте прав на зміну цього рівня.'}, status=403)

    change.status = 'rejected'
    change.save()

    return Response({'detail': 'Зміни було відхилено.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_level(request, level_id):
    try:
        level = Level.objects.get(id=level_id)
    except Level.DoesNotExist:
        return Response({'detail': 'Рівень не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

    if level.author != request.user:
        return Response({'detail': 'Ви не можете видалити цей рівень.'}, status=status.HTTP_403_FORBIDDEN)

    level.delete()
    return Response({'detail': 'Рівень успішно видалено.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_level(request, level_id):
    try:
        level = Level.objects.get(id=level_id)
    except Level.DoesNotExist:
        return Response({'detail': 'Рівень не знайдено.'}, status=404)

    if level.author != request.user:
        return Response({'detail': 'Ви не маєте прав редагувати цей рівень.'}, status=403)

    data = request.data

    if 'title' in data:
        level.title = data['title']
    if 'description' in data:
        level.description = data['description']
    if 'data' in data:
        level.data = data['data']
    if 'is_public' in data:
        level.is_public = data['is_public']

    level.save()
    return Response({'detail': 'Рівень успішно оновлено.'})