from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .models import PaymentPlan, Installment
from .serializers import PaymentPlanCreateSerializer, PaymentPlanListSerializer, InstallmentPaySerializer, InstallmentSerializer
from .services import pay_installment
from django.contrib.auth import get_user_model
from django.http import Http404

User = get_user_model()

class IsMerchantUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Merchant').exists() 
        )

class IsUserInUserGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='User').exists()
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

class InstallmentPayView(generics.CreateAPIView):
    serializer_class = InstallmentPaySerializer
    permission_classes = [permissions.IsAuthenticated, IsUserInUserGroup]
    queryset = Installment.objects.all()
    lookup_url_kwarg = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        installment_id = self.kwargs.get('id')
        try:
            context['installment'] = self.queryset.get(id=installment_id)
        except Installment.DoesNotExist:
            raise Http404("Installment not found")
        return context

    def create(self, request, *args, **kwargs):
        installment_id = self.kwargs.get('id')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_installment = pay_installment(installment_id, request.user.id)
            return Response(InstallmentSerializer(updated_installment).data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
