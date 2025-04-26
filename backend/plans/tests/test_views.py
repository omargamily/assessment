from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
from ..models import PaymentPlan, Installment

User = get_user_model()

class PaymentPlanCreateViewTests(APITestCase):
    def setUp(self):
        # Create necessary groups
        self.merchant_group = Group.objects.create(name='Merchant')
        self.user_group = Group.objects.create(name='User')

        # Create a merchant user
        self.merchant = User.objects.create_user(
            email='merchant@test.com',
            password='password123',
            role='merchant'
        )
        self.merchant.groups.add(self.merchant_group)

        # Create a regular user
        self.user = User.objects.create_user(
            email='user@test.com',
            password='password123',
            role='user'
        )
        self.user.groups.add(self.user_group)

        # Create another merchant for testing unauthorized access
        self.other_merchant = User.objects.create_user(
            email='other.merchant@test.com',
            password='password123',
            role='merchant'
        )
        self.other_merchant.groups.add(self.merchant_group)

        self.valid_data = {
        'user': self.user.pk, 
        'total_amount': '1000.00',
        'number_of_installments': 5,
        'start_date': (timezone.now().date() + timedelta(days=1)).isoformat()
    }

        # URL for creating payment plans
        self.url = reverse('plans:create-payment-plan')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot create payment plans"""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_merchant_access(self):
        """Test that non-merchant users cannot create payment plans"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_payment_plan_creation(self):
        """Test successful creation of a payment plan by a merchant"""
        self.client.force_authenticate(user=self.merchant)
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify plan was created in database
        plan = PaymentPlan.objects.get(id=response.data['id'])
        self.assertEqual(plan.merchant, self.merchant)
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.total_amount, Decimal(self.valid_data['total_amount']))
        self.assertEqual(plan.number_of_installments, self.valid_data['number_of_installments'])
        
        # Verify installments were created
        installments = plan.installments.all()
        self.assertEqual(installments.count(), self.valid_data['number_of_installments'])

    def test_invalid_user_id(self):
        """Test validation of invalid user_id"""
        self.client.force_authenticate(user=self.merchant)
        invalid_data = self.valid_data.copy()
        invalid_data['user'] = '12345678-1234-5678-1234-567812345678'  # Random UUID
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid pk "12345678-1234-5678-1234-567812345678"', str(response.data['user'][0]))

    def test_past_start_date(self):
        """Test validation of past start date"""
        self.client.force_authenticate(user=self.merchant)
        invalid_data = self.valid_data.copy()
        invalid_data['start_date'] = (timezone.now().date() - timedelta(days=1)).isoformat()
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data)

    def test_zero_installments(self):
        """Test validation of zero installments"""
        self.client.force_authenticate(user=self.merchant)
        invalid_data = self.valid_data.copy()
        invalid_data['number_of_installments'] = 0
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('number_of_installments', response.data)

    def test_negative_amount(self):
        """Test validation of negative amount"""
        self.client.force_authenticate(user=self.merchant)
        invalid_data = self.valid_data.copy()
        invalid_data['total_amount'] = '-1000.00'
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('total_amount', response.data)

    def test_missing_required_fields(self):
        """Test validation of missing required fields"""
        self.client.force_authenticate(user=self.merchant)
        invalid_data = {}
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        required_fields = ['user', 'total_amount', 'number_of_installments', 'start_date']
        for field in required_fields:
            self.assertIn(field, response.data)

    def test_get_method_not_allowed(self):
        """Test that GET method is not allowed"""
        self.client.force_authenticate(user=self.merchant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)