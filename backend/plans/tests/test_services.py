from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from plans.services import create_payment_plan, update_installment_statuses
from plans.models import PaymentPlan, Installment
from dateutil.relativedelta import relativedelta
from django.db import transaction

User = get_user_model()

class CreatePaymentPlanServiceTests(TestCase):
    def setUp(self):
        # Create test users
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

        self.start_date = timezone.now().date()
        self.total_amount = Decimal('1000.00')
        self.number_of_installments = 4

    def test_create_payment_plan_success(self):
        """Test successful payment plan creation with correct installments"""
        plan = create_payment_plan(
            merchant=self.merchant,
            user=self.user,
            total_amount=self.total_amount,
            number_of_installments=self.number_of_installments,
            start_date=self.start_date
        )

        # Verify plan details
        self.assertIsNotNone(plan)
        self.assertEqual(plan.merchant, self.merchant)
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.total_amount, self.total_amount)
        self.assertEqual(plan.number_of_installments, self.number_of_installments)
        self.assertEqual(plan.status, 'Active')

        # Verify installments
        installments = plan.installments.all().order_by('due_date')
        self.assertEqual(installments.count(), self.number_of_installments)

        # Check installment amounts sum up to total
        total_installments = sum(inst.amount for inst in installments)
        self.assertEqual(total_installments, self.total_amount)

        # Verify installment dates
        for i, installment in enumerate(installments):
            expected_date = self.start_date + relativedelta(months=i)
            self.assertEqual(installment.due_date, expected_date)
            self.assertEqual(installment.status, 'Pending')

    def test_create_payment_plan_odd_amount_distribution(self):
        """Test payment plan creation with amount that doesn't divide evenly"""
        odd_amount = Decimal('100.01')
        plan = create_payment_plan(
            merchant=self.merchant,
            user=self.user,
            total_amount=odd_amount,
            number_of_installments=3,
            start_date=self.start_date
        )

        installments = plan.installments.all().order_by('due_date')
        
        # Check first two installments are equal
        self.assertEqual(installments[0].amount, installments[1].amount)
        
        # Verify last installment handles the remainder
        total_installments = sum(inst.amount for inst in installments)
        self.assertEqual(total_installments, odd_amount)
        
        # Verify no rounding errors
        self.assertEqual(len(str(total_installments).split('.')[-1]), 2)

    def test_create_payment_plan_transaction_rollback(self):
        """Test transaction rollback when an error occurs during installment creation"""
        initial_plan_count = PaymentPlan.objects.count()
        initial_installment_count = Installment.objects.count()

        # Mock scenario where installment creation fails
        with self.assertRaises(Exception):
            with transaction.atomic():
                create_payment_plan(
                    merchant=self.merchant,
                    user=self.user,
                    total_amount=self.total_amount,
                    number_of_installments=self.number_of_installments,
                    start_date=self.start_date
                )
                # Simulate an error after plan creation but before installment creation
                raise Exception("Simulated error")

        # Verify no objects were created due to transaction rollback
        self.assertEqual(PaymentPlan.objects.count(), initial_plan_count)
        self.assertEqual(Installment.objects.count(), initial_installment_count)

    def test_create_payment_plan_with_single_installment(self):
        """Test payment plan creation with a single installment"""
        plan = create_payment_plan(
            merchant=self.merchant,
            user=self.user,
            total_amount=self.total_amount,
            number_of_installments=1,
            start_date=self.start_date
        )

        installments = plan.installments.all()
        self.assertEqual(installments.count(), 1)
        self.assertEqual(installments[0].amount, self.total_amount)
        self.assertEqual(installments[0].due_date, self.start_date)

    def test_create_payment_plan_decimal_precision(self):
        """Test payment plan handles decimal precision correctly"""
        precise_amount = Decimal('1000.57')
        plan = create_payment_plan(
            merchant=self.merchant,
            user=self.user,
            total_amount=precise_amount,
            number_of_installments=3,
            start_date=self.start_date
        )

        installments = plan.installments.all()
        total = sum(inst.amount for inst in installments)
        
        # Verify total matches exactly
        self.assertEqual(total, precise_amount)
        
        # Verify each installment has max 2 decimal places
        for inst in installments:
            decimal_places = len(str(inst.amount).split('.')[-1])
            self.assertLessEqual(decimal_places, 2)

    def test_create_payment_plan_date_progression(self):
        """Test installment dates progress correctly monthly"""
        plan = create_payment_plan(
            merchant=self.merchant,
            user=self.user,
            total_amount=self.total_amount,
            number_of_installments=12,
            start_date=self.start_date
        )

        installments = plan.installments.all().order_by('due_date')
        
        # Verify monthly progression
        for i, installment in enumerate(installments):
            if i > 0:
                prev_date = installments[i-1].due_date
                expected_date = prev_date + relativedelta(months=1)
                self.assertEqual(installment.due_date, expected_date)

    def test_create_payment_plan_with_zero_amount(self):
        """Test payment plan creation fails with zero amount"""
        with self.assertRaises(Exception):
            create_payment_plan(
                merchant=self.merchant,
                user=self.user,
                total_amount=Decimal('0.00'),
                number_of_installments=self.number_of_installments,
                start_date=self.start_date
            )

class UpdateInstallmentStatusesTests(TestCase):
    def setUp(self):
        # Create test users
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

        self.today = timezone.now().date()
        
        # Create a payment plan with installments,
        self.plan = PaymentPlan.objects.create(
            merchant=self.merchant,
            user=self.user,
            total_amount=Decimal('1000.00'),
            number_of_installments=4,
            start_date=self.today - relativedelta(days=30)
        )
        
    def tearDown(self):
        Installment.objects.all().delete()  # Clear existing installments
        return super().tearDown()

    def test_update_installment_statuses(self):
        """Test that installment statuses are correctly updated based on due dates"""
        # Create installments with different due dates
        past_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today - relativedelta(days=5),
            amount=Decimal('250.00'),
            status='Pending'
        )
        
        due_today_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today,
            amount=Decimal('250.00'),
            status='Pending'
        )
        
        future_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today + relativedelta(days=5),
            amount=Decimal('250.00'),
            status='Pending'
        )
        
        # Run the update function
        updated_count = update_installment_statuses()
        
        # Refresh installments from database
        past_installment.refresh_from_db()
        due_today_installment.refresh_from_db()
        future_installment.refresh_from_db()
        
        # Assert statuses are updated correctly
        self.assertEqual(past_installment.status, 'Late')
        self.assertEqual(due_today_installment.status, 'Due')
        self.assertEqual(future_installment.status, 'Pending')
        self.assertEqual(updated_count, 2)  # 2 installments should have been updated

    def test_already_updated_installments(self):
        """Test that already updated installments are not updated again"""
        late_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today - relativedelta(days=5),
            amount=Decimal('250.00'),
            status='Late'
        )
        
        # Run the update function
        updated_count = update_installment_statuses()
        
        # Refresh installment from database
        late_installment.refresh_from_db()
        
        # Assert status hasn't changed and no installments were updated
        self.assertEqual(late_installment.status, 'Late')
        self.assertEqual(updated_count, 0)

    def test_paid_installments_not_updated(self):
        """Test that paid installments are not updated even if overdue"""
        paid_installment = Installment.objects.create(
            plan=self.plan,
            due_date=self.today - relativedelta(days=5),
            amount=Decimal('250.00'),
            status='Paid'
        )
        
        # Run the update function
        updated_count = update_installment_statuses()
        
        # Refresh installment from database
        paid_installment.refresh_from_db()
        
        # Assert status hasn't changed and no installments were updated
        self.assertEqual(paid_installment.status, 'Paid')
        self.assertEqual(updated_count, 0)