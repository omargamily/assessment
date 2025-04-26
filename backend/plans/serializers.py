from rest_framework import serializers
from plans.models.installment import Installment
from .models import PaymentPlan
from django.contrib.auth import get_user_model
from .services import create_payment_plan
from decimal import Decimal
from .validators import validate_plan_creation_data
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class PaymentPlanCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='user'),
        write_only=True
    )
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = PaymentPlan
        fields = [
            'id',
            'user',
            'total_amount',
            'number_of_installments',
            'start_date',
        ]
        read_only_fields = ['merchant', 'status']

    def validate(self, data):
        try:
            validate_plan_creation_data(
                total_amount=data.get('total_amount'),
                number_of_installments=data.get('number_of_installments'),
                start_date=data.get('start_date')
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)

        return data


    def create(self, validated_data):
        merchant_instance = validated_data.pop('merchant')
        user_instance = validated_data.pop('user')
        plan = create_payment_plan(
            merchant=merchant_instance,
            user=user_instance,
            **validated_data
        )
        return plan
class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ['id', 'due_date', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = fields
class PaymentPlanListSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    merchant_email = serializers.EmailField(source='merchant.email', read_only=True)


    class Meta:
        model = PaymentPlan
        fields = [
            'id',
            'merchant_email',
            'user_email',    
            'total_amount',
            'number_of_installments',
            'start_date',
            'status',
            'created_at',
            'updated_at',
            'installments' 
        ]
        read_only_fields = fields

class InstallmentPaySerializer(serializers.Serializer):
    def validate(self, attrs):
        # Get installment from view context
        installment = self.context.get('installment')
        if not installment:
            raise serializers.ValidationError("Installment not found")

        # Validate installment belongs to user
        user = self.context.get('request').user
        if installment.plan.user_id != user.id:
            raise serializers.ValidationError("This installment does not belong to you")
        
        # Validate installment status is valid for payment
        if installment.status == 'Paid':
            raise serializers.ValidationError("This installment is already paid")
        
        if installment.status not in ['Pending', 'Due', 'Late']:
            raise serializers.ValidationError("Invalid installment status for payment")

        return attrs
