from django.urls import path
from .views import upload_level, public_levels, get_level_by_id, propose_change, view_change_requests, accept_change, reject_change, public_levels_by_author, delete_level, edit_level, get_change_request_by_id

urlpatterns = [
    path('upload/', upload_level, name='upload_level'),
    path('public/', public_levels, name='public_levels'),
    path('<int:level_id>/', get_level_by_id, name='get_level_by_id'),
    path('<int:level_id>/propose-change/', propose_change),
    path('changes/', view_change_requests),
    path('changes/<int:change_id>/', get_change_request_by_id),
    path('<int:level_id>/changes/<int:change_id>/accept/', accept_change),
    path('<int:level_id>/changes/<int:change_id>/reject/', reject_change),
    path('public/by-author/<str:username>/', public_levels_by_author, name='public_levels_by_author'),
    path('<int:level_id>/delete/', delete_level, name='delete_level'),
    path('<int:level_id>/edit/', edit_level, name='edit_level'),
]