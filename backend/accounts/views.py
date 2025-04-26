from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer

# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
