from django.urls import path
from .views import UserList, UserDetail

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<str:username>/', UserDetail.as_view(), name='user-detail'),
]
