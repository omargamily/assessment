# plans/serializers.py
from rest_framework import serializers
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
