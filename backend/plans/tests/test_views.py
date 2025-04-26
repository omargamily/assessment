from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
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
        
class PaymentPlanListViewTests(APITestCase):
    def setUp(self):
        self.merchant_group, _ = Group.objects.get_or_create(name='Merchant')
        self.user_group, _ = Group.objects.get_or_create(name='User')

        self.merchant1 = User.objects.create_user(email='m1@test.com', password='p', role='merchant')
        self.merchant1.groups.add(self.merchant_group)
        self.merchant2 = User.objects.create_user(email='m2@test.com', password='p', role='merchant')
        self.merchant2.groups.add(self.merchant_group)

        self.user1 = User.objects.create_user(email='u1@test.com', password='p', role='user')
        self.user1.groups.add(self.user_group)
        self.user2 = User.objects.create_user(email='u2@test.com', password='p', role='user')
        self.user2.groups.add(self.user_group)

        self.other_user = User.objects.create_user(email='other@test.com', password='p', role='staff')
        start_date = date(2025, 5, 1)

        self.plan_m1_u1 = PaymentPlan.objects.create(
            merchant=self.merchant1, user=self.user1, total_amount=Decimal('100.00'),
            number_of_installments=2, start_date=start_date
        )
        Installment.objects.create(plan=self.plan_m1_u1, due_date=start_date, amount=Decimal('50.00'))
        Installment.objects.create(plan=self.plan_m1_u1, due_date=start_date + timedelta(days=30), amount=Decimal('50.00'))

        self.plan_m1_u2 = PaymentPlan.objects.create(
            merchant=self.merchant1, user=self.user2, total_amount=Decimal('200.00'),
            number_of_installments=1, start_date=start_date
        )
        Installment.objects.create(plan=self.plan_m1_u2, due_date=start_date, amount=Decimal('200.00'))


        self.plan_m2_u1 = PaymentPlan.objects.create(
            merchant=self.merchant2, user=self.user1, total_amount=Decimal('300.00'),
            number_of_installments=3, start_date=start_date
        )
        Installment.objects.create(plan=self.plan_m2_u1, due_date=start_date, amount=Decimal('100.00'))
        Installment.objects.create(plan=self.plan_m2_u1, due_date=start_date + timedelta(days=30), amount=Decimal('100.00'))
        Installment.objects.create(plan=self.plan_m2_u1, due_date=start_date + timedelta(days=60), amount=Decimal('100.00'))

        self.url = reverse('plans:list-payment-plans')

    def test_unauthenticated_cannot_list_plans(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_roles_get_empty_list(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_merchant_sees_only_own_created_plans(self):
        self.client.force_authenticate(user=self.merchant1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        plan_ids_in_response = {str(plan['id']) for plan in response.data}
        expected_plan_ids = {str(self.plan_m1_u1.id), str(self.plan_m1_u2.id)}

        self.assertSetEqual(plan_ids_in_response, expected_plan_ids)
        self.assertNotIn(str(self.plan_m2_u1.id), plan_ids_in_response)

    def test_user_sees_only_own_assigned_plans(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        plan_ids_in_response = {str(plan['id']) for plan in response.data}
        expected_plan_ids = {str(self.plan_m1_u1.id), str(self.plan_m2_u1.id)}

        self.assertSetEqual(plan_ids_in_response, expected_plan_ids)
        self.assertNotIn(str(self.plan_m1_u2.id), plan_ids_in_response)

    def test_user_sees_nested_installments(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Find plan for merchant2 (m2@test.com)
        m2_plan = next((p for p in response.data if p['merchant_email'] == 'm2@test.com'), None)
        self.assertIsNotNone(m2_plan, "Plan from merchant2 not found")
        self.assertEqual(len(m2_plan['installments']), 3)
        for installment in m2_plan['installments']:
            self.assertEqual(Decimal(installment['amount']), Decimal('100.00'))

        # Find plan for merchant1 (m1@test.com)
        m1_plan = next((p for p in response.data if p['merchant_email'] == 'm1@test.com'), None)
        self.assertIsNotNone(m1_plan, "Plan from merchant1 not found")
        self.assertEqual(len(m1_plan['installments']), 2)
        for installment in m1_plan['installments']:
            self.assertEqual(Decimal(installment['amount']), Decimal('50.00'))

    def test_merchant_with_no_plans_gets_empty_list(self):
        merchant3 = User.objects.create_user(email='m3_empty@test.com', password='p', role='merchant')
        merchant3.groups.add(self.merchant_group)
        self.client.force_authenticate(user=merchant3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_user_with_no_plans_gets_empty_list(self):
        user3 = User.objects.create_user(email='u3_empty@test.com', password='p', role='user')
        user3.groups.add(self.user_group)
        self.client.force_authenticate(user=user3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_serializer_output_fields(self):
        self.client.force_authenticate(user=self.merchant1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0, "Serializer output test requires at least one plan in the response.")
        plan_data = response.data[0]

        expected_plan_keys = [
            'id', 'merchant_email', 'user_email', 'total_amount',
            'number_of_installments', 'start_date', 'status',
            'created_at', 'updated_at', 'installments'
        ]
        self.assertCountEqual(plan_data.keys(), expected_plan_keys)

        self.assertGreater(len(plan_data.get('installments', [])), 0, "Serializer output test requires at least one installment in the plan.")
        installment_data = plan_data['installments'][0]
        expected_installment_keys = [
            'id', 'due_date', 'amount', 'status', 'created_at', 'updated_at'
        ]
        self.assertCountEqual(installment_data.keys(), expected_installment_keys)
        self.assertEqual(plan_data['merchant_email'], self.merchant1.email)
