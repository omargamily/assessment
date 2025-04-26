from rest_framework import generics, permissions
from .models import PaymentPlan
from .serializers import PaymentPlanCreateSerializer, PaymentPlanListSerializer
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
        
class PaymentPlanListView(generics.ListAPIView):
    serializer_class = PaymentPlanListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = PaymentPlan.objects.none()

        # Check user group membership for filtering
        if user.groups.filter(name='Merchant').exists():
            # Merchants see plans they created
            queryset = PaymentPlan.objects.filter(merchant=user)
        elif user.groups.filter(name='User').exists():
            # Users see plans assigned to them
            queryset = PaymentPlan.objects.filter(user=user)

        return queryset.prefetch_related('installments').order_by('-created_at')
