from django.urls import path
from .views import protected_view, register_user, delete_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', protected_view),
    path('register/', register_user, name='register_user'),
    path('delete/', delete_user, name='delete_user'),
]