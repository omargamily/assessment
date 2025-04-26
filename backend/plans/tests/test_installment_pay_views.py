from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from plans.models import PaymentPlan, Installment

User = get_user_model()

class InstallmentPayViewTests(APITestCase):
    def setUp(self):
        # Create groups
        self.merchant_group = Group.objects.create(name='Merchant')
        self.user_group = Group.objects.create(name='User')

        # Create users
        self.merchant = User.objects.create_user(
            email='merchant@test.com',
            password='password123',
            role='merchant'
        )
        self.merchant.groups.add(self.merchant_group)

        self.user = User.objects.create_user(
            email='user@test.com',
            password='password123',
            role='user'
        )
        self.user.groups.add(self.user_group)

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='password123',
            role='user'
        )
        self.other_user.groups.add(self.user_group)

        # Create a payment plan
        self.plan = PaymentPlan.objects.create(
            merchant=self.merchant,
            user=self.user,
            total_amount=Decimal('1000.00'),
            number_of_installments=4,
            start_date=date.today()
        )

        # Create installments
        self.installments = []
        statuses = ['Pending', 'Due', 'Late', 'Paid']
        for i, status in enumerate(statuses):
            installment = Installment.objects.create(
                plan=self.plan,
                due_date=date.today() + timedelta(days=30*i),
                amount=Decimal('250.00'),
                status=status
            )
            self.installments.append(installment)

    def get_pay_url(self, installment_id):
        return reverse('plans:pay-installment', kwargs={'id': installment_id})

    def test_successful_payment(self):
        """Test successful payment of a pending installment"""
        self.client.force_authenticate(user=self.user)
        pending_installment = next(i for i in self.installments if i.status == 'Pending')
        
        response = self.client.post(self.get_pay_url(pending_installment.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify installment status updated
        pending_installment.refresh_from_db()
        self.assertEqual(pending_installment.status, 'Paid')

    def test_successful_payment_updates_plan(self):
        """Test plan status updates to Paid when all installments are paid"""
        self.client.force_authenticate(user=self.user)
        
        # Pay all unpaid installments
        for installment in self.installments:
            if installment.status != 'Paid':
                response = self.client.post(self.get_pay_url(installment.id))
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify plan status is updated
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.status, 'Paid')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot pay installments"""
        pending_installment = next(i for i in self.installments if i.status == 'Pending')
        response = self.client.post(self.get_pay_url(pending_installment.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user_access(self):
        """Test that other users cannot pay installments they don't own"""
        self.client.force_authenticate(user=self.other_user)
        pending_installment = next(i for i in self.installments if i.status == 'Pending')
        
        response = self.client.post(self.get_pay_url(pending_installment.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This installment does not belong to you', str(response.data))

    def test_already_paid_installment(self):
        """Test that already paid installments cannot be paid again"""
        self.client.force_authenticate(user=self.user)
        paid_installment = next(i for i in self.installments if i.status == 'Paid')
        
        response = self.client.post(self.get_pay_url(paid_installment.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already paid', str(response.data))

    def test_nonexistent_installment(self):
        """Test paying a non-existent installment"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('plans:pay-installment', kwargs={'id': '12345678-1234-5678-1234-567812345678'})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_merchant_cannot_pay(self):
        """Test that merchants cannot pay installments"""
        self.client.force_authenticate(user=self.merchant)
        pending_installment = next(i for i in self.installments if i.status == 'Pending')
        
        response = self.client.post(self.get_pay_url(pending_installment.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)