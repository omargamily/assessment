from rest_framework import generics, permissions
from .serializers import UserDetailSerializer, UserRegistrationSerializer, UserListSerializer
from .permissions import IsMerchantRole
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMerchantRole]
    serializer_class = UserListSerializer
    queryset = User.objects.filter(role='user')

class MeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user