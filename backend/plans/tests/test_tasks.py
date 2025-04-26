# plans/tests/test_tasks.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from plans.models import PaymentPlan, Installment
from plans.tasks import update_installment_statuses_task, check_upcoming_installments_task
from unittest.mock import patch, Mock
from datetime import date, timedelta
from freezegun import freeze_time

User = get_user_model()

FROZEN_TIME_STR = "2025-04-26 10:00:00"
FROZEN_DATE = date(2025, 4, 26)

@freeze_time(FROZEN_TIME_STR)
class UpdateInstallmentStatusesTaskTests(TestCase):
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
        self.today = FROZEN_DATE
        self.plan = PaymentPlan.objects.create(
            merchant=self.merchant,
            user=self.user,
            total_amount=Decimal('1000.00'),
            number_of_installments=4,
            start_date=self.today - timedelta(days=30)
        )
        
    def test_task_execution(self):
        """Test that the Celery task executes successfully with frozen time"""
        past_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today - timedelta(days=5),
            amount=Decimal('250.00'),
            status='Pending'
        )
        due_today_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today,
            amount=Decimal('250.00'),
            status='Pending'
        )
        result = update_installment_statuses_task.apply()
        past_installment.refresh_from_db()
        due_today_installment.refresh_from_db()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(), 2) 

        self.assertEqual(past_installment.status, 'Late')
        self.assertEqual(due_today_installment.status, 'Due')

    @patch('plans.tasks.update_installment_statuses')
    def test_task_error_handling(self, mock_update):
        """Test that task handles errors appropriately"""
        mock_update.side_effect = Exception('Test error')

        with self.assertRaises(Exception):
            update_installment_statuses_task()

        mock_update.assert_called_once() 

    def test_check_upcoming_installments(self):
        """Test that upcoming installments are correctly identified with frozen time"""
        # Calculate future date relative to the frozen date
        three_days_future = self.today + timedelta(days=3)
        upcoming_installment = Installment.objects.create(
            plan=self.plan,
            due_date=three_days_future,
            amount=Decimal('250.00'),
            status='Pending'
        )
        five_days_future = self.today + timedelta(days=5)
        Installment.objects.create(
            plan=self.plan,
            due_date=five_days_future,
            amount=Decimal('250.00'),
            status='Pending'
        )
        with self.assertLogs('plans.tasks', level='INFO') as logs:
            result = check_upcoming_installments_task.apply()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(), 1) 
        log_output = '\n'.join(logs.output)
        self.assertIn(f"User {self.user.email}", log_output)
        self.assertIn("due in 3 days", log_output)
        self.assertIn(f"Due date: {three_days_future}", log_output)
        self.assertIn(str(upcoming_installment.amount), log_output)

    def test_no_upcoming_installments(self):
        """Test behavior when there are no upcoming installments with frozen time"""
        ten_days_future = self.today + timedelta(days=10)
        future_installment = Installment.objects.create(
            plan=self.plan,
            due_date=ten_days_future,
            amount=Decimal('250.00'),
            status='Pending'
        )
        result = check_upcoming_installments_task.apply()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(), 0)

    def test_multiple_upcoming_installments_notifications(self):
        """Test handling multiple upcoming installments for different users with frozen time"""
        another_user = User.objects.create_user(
            email='another@test.com',
            password='password123',
            role='user'
        )

        another_plan = PaymentPlan.objects.create(
            merchant=self.merchant,
            user=another_user,
            total_amount=Decimal('2000.00'),
            number_of_installments=4,
            start_date=self.today - timedelta(days=15)
        )
        three_days_future = self.today + timedelta(days=3)
        upcoming_installment1 = Installment.objects.create(
            plan=self.plan,
            due_date=three_days_future,
            amount=Decimal('250.00'),
            status='Pending'
        )

        upcoming_installment2 = Installment.objects.create(
            plan=another_plan,
            due_date=three_days_future,
            amount=Decimal('500.00'),
            status='Pending'
        )
        with self.assertLogs('plans.tasks', level='INFO') as logs:
            result = check_upcoming_installments_task.apply()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(), 2)
        log_output = '\n'.join(logs.output)
        self.assertIn(str(upcoming_installment1.amount), log_output)
        self.assertIn(str(upcoming_installment2.amount), log_output)
        self.assertIn(self.user.email, log_output)
        self.assertIn(another_user.email, log_output)
        self.assertEqual(log_output.count("UPCOMING INSTALLMENT NOTIFICATION:"), 2)


    def test_paid_installment_not_in_upcoming(self):
        """Test that paid installments are not included in upcoming notifications with frozen time"""
        three_days_future = self.today + timedelta(days=3)
        paid_installment = Installment.objects.create(
            plan=self.plan,
            due_date=three_days_future,
            amount=Decimal('250.00'),
            status='Paid' 
        )
        result = check_upcoming_installments_task.apply()
        self.assertTrue(result.successful())
        self.assertEqual(result.get(), 0)