from rest_framework import generics, permissions
from .models import PaymentPlan
from .serializers import PaymentPlanCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class IsMerchantUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Merchant').exists() 
        )


class PaymentPlanCreateView(generics.CreateAPIView):
    serializer_class = PaymentPlanCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsMerchantUser]

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user)