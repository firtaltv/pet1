from django.urls import path
from .views import UserProfileAPIView

app_name = 'users'

urlpatterns = [
    path('', UserProfileAPIView.as_view(), name='user_profile'),
]
