from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer, UserListSerializer
from .permissions import IsMerchantGroup
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMerchantGroup]
    serializer_class = UserListSerializer
    queryset = User.objects.filter(role='user')
