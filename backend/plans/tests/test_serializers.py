# plans/tests/test_serializers.py
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from plans.serializers import PaymentPlanCreateSerializer
from plans.models import PaymentPlan
from decimal import Decimal
from unittest.mock import patch, MagicMock # Import MagicMock
from datetime import date, timedelta

User = get_user_model()

class PaymentPlanCreateSerializerTests(TestCase):
    def setUp(self):
        self.merchant = User.objects.create_user(
            email='merchant@test.com',
            password='password123',
            role='merchant'
        )
        self.user = User.objects.create_user(
            email='user@test.com',
            password='password123',
            role='user'
        )
        self.valid_data = {
            'user': self.user.pk,
            'total_amount': Decimal('1000.00'),
            'number_of_installments': 5,
            'start_date': (timezone.now().date() + timedelta(days=1))
        }
        self.mock_request = MagicMock()
        self.mock_request.user = self.merchant
        self.serializer_context = {
            'request': self.mock_request
        }

    def test_serializer_valid_data(self):
        serializer = PaymentPlanCreateSerializer(
            data=self.valid_data,
            context=self.serializer_context
        )
        is_valid = serializer.is_valid()
        if not is_valid:
            print(f"Serializer errors: {serializer.errors}")
        self.assertTrue(is_valid)
        self.assertEqual(len(serializer.errors), 0)
        
    @patch('plans.serializers.create_payment_plan')
    def test_create_payment_plan(self, mock_create_payment_plan):
        mock_plan = PaymentPlan(id=1, merchant=self.merchant, user=self.user)
        mock_create_payment_plan.return_value = mock_plan

        serializer = PaymentPlanCreateSerializer(
            data=self.valid_data,
            context=self.serializer_context
        )
        
        serializer.is_valid(raise_exception=True)
        created_plan = serializer.save(merchant=self.merchant) 

        mock_create_payment_plan.assert_called_once_with(
            merchant=self.merchant,
            user=self.user,
            total_amount=self.valid_data['total_amount'],
            number_of_installments=self.valid_data['number_of_installments'],
            start_date=self.valid_data['start_date']
        )
        self.assertEqual(created_plan, mock_plan)


    def test_read_only_fields(self):
        data_with_readonly = self.valid_data.copy()
        data_with_readonly.update({
            'merchant': self.merchant.pk,
            'status': 'Paid',
        })
        
        serializer = PaymentPlanCreateSerializer(
            data=data_with_readonly,
            context=self.serializer_context
        )
        is_valid = serializer.is_valid()
        if not is_valid:
             print(f"Read only test errors: {serializer.errors}")
        self.assertTrue(is_valid)
        self.assertNotIn('merchant', serializer.validated_data)
        self.assertNotIn('status', serializer.validated_data)
        self.assertIn('user', serializer.validated_data)
        self.assertIn('total_amount', serializer.validated_data)
        self.assertIn('number_of_installments', serializer.validated_data)
        self.assertIn('start_date', serializer.validated_data)

    def test_serializer_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data['start_date'] = timezone.now().date() - timedelta(days=1)

        serializer = PaymentPlanCreateSerializer(
            data=invalid_data,
            context=self.serializer_context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('start_date', serializer.errors)
        
    def test_serializer_invalid_user_pk(self):
        invalid_data = self.valid_data.copy()
        invalid_data['user'] = 999999 

        serializer = PaymentPlanCreateSerializer(
            data=invalid_data,
            context=self.serializer_context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)
        
    def test_serializer_user_is_merchant(self):
        invalid_data = self.valid_data.copy()
        invalid_data['user'] = self.merchant.pk

        serializer = PaymentPlanCreateSerializer(
            data=invalid_data,
            context=self.serializer_context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)