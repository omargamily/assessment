from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from accounts.permissions import IsMerchantRole, IsUserRole, IsOwnerOrMerchantOfPlan
from .models import PaymentPlan, Installment
from .serializers import PaymentPlanCreateSerializer, PaymentPlanListSerializer, InstallmentPaySerializer, InstallmentSerializer
from .services import pay_installment
from django.contrib.auth import get_user_model
from django.http import Http404

User = get_user_model()


class PaymentPlanCreateView(generics.CreateAPIView):
    serializer_class = PaymentPlanCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsMerchantRole]

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user)


class PaymentPlanListView(generics.ListAPIView):
    serializer_class = PaymentPlanListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = PaymentPlan.objects.none()

        if user.role == 'merchant':
            queryset = PaymentPlan.objects.filter(merchant=user)
        elif user.role == 'user':
            queryset = PaymentPlan.objects.filter(user=user)

        return queryset.prefetch_related('installments').order_by('-created_at')


class PaymentPlanDetailView(generics.RetrieveAPIView):
    queryset = PaymentPlan.objects.all().prefetch_related('installments')
    serializer_class = PaymentPlanListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMerchantOfPlan]
    lookup_field = 'id'


class InstallmentPayView(generics.CreateAPIView):
    serializer_class = InstallmentPaySerializer
    permission_classes = [permissions.IsAuthenticated, IsUserRole]
    queryset = Installment.objects.all()
    lookup_url_kwarg = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context

        installment_id = self.kwargs.get('id')
        if installment_id:
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