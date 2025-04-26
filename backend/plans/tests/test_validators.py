# plans/tests/test_validators.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from plans.validators import validate_plan_creation_data

class PlanCreationValidatorTests(TestCase):

    def setUp(self):
        self.valid_total_amount = Decimal('1000.00')
        self.valid_number_of_installments = 5
        self.valid_start_date = timezone.now().date() + timedelta(days=1)

    def test_validator_valid_data(self):
        try:
            validate_plan_creation_data(
                total_amount=self.valid_total_amount,
                number_of_installments=self.valid_number_of_installments,
                start_date=self.valid_start_date
            )
        except ValidationError:
            self.fail("validate_plan_creation_data raised ValidationError unexpectedly!")

    def test_validator_start_date_past(self):
        past_date = timezone.now().date() - timedelta(days=1)
        with self.assertRaisesRegex(ValidationError, 'Start date cannot be in the past.'):
            validate_plan_creation_data(
                total_amount=self.valid_total_amount,
                number_of_installments=self.valid_number_of_installments,
                start_date=past_date
            )

    def test_validator_number_of_installments_zero(self):
        with self.assertRaisesRegex(ValidationError, 'Number of installments must be a positive integer.'):
            validate_plan_creation_data(
                total_amount=self.valid_total_amount,
                number_of_installments=0,
                start_date=self.valid_start_date
            )

    def test_validator_number_of_installments_negative(self):
        with self.assertRaisesRegex(ValidationError, 'Number of installments must be a positive integer.'):
            validate_plan_creation_data(
                total_amount=self.valid_total_amount,
                number_of_installments=-1,
                start_date=self.valid_start_date
            )

    def test_validator_total_amount_zero(self):
        with self.assertRaisesRegex(ValidationError, 'Total amount must be positive.'):
             validate_plan_creation_data(
                total_amount=Decimal('0.00'),
                number_of_installments=self.valid_number_of_installments,
                start_date=self.valid_start_date
            )

    def test_validator_total_amount_negative(self):
        with self.assertRaisesRegex(ValidationError, 'Total amount must be positive.'):
             validate_plan_creation_data(
                total_amount=Decimal('-100.00'),
                number_of_installments=self.valid_number_of_installments,
                start_date=self.valid_start_date
            )
            
    def test_validator_total_amount_invalid_type(self):
        with self.assertRaisesRegex(ValidationError, 'Invalid value provided for total amount.'):
             validate_plan_creation_data(
                total_amount='not-a-decimal',
                number_of_installments=self.valid_number_of_installments,
                start_date=self.valid_start_date
            )