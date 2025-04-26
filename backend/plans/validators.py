# plans/validators.py
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_plan_creation_data(total_amount, number_of_installments, start_date):
    """
    Performs common validation checks for payment plan creation data.
    Raises django.core.exceptions.ValidationError if checks fail.
    """
    errors = {}
    
    # Validate total_amount
    if not isinstance(total_amount, Decimal):
        try:
            total_amount = Decimal(total_amount)
        except InvalidOperation:
             errors['total_amount'] = "Invalid value provided for total amount."
             total_amount = None 
             
    if total_amount is not None and total_amount <= Decimal('0.00'):
        errors['total_amount'] = "Total amount must be positive."

    # Validate number_of_installments
    if not isinstance(number_of_installments, int) or number_of_installments <= 0:
        errors['number_of_installments'] = "Number of installments must be a positive integer."

    # Validate start_date
    # Ensure start_date is a date object for comparison
    if hasattr(start_date, 'date'):
        start_date = start_date.date()
        
    if start_date < timezone.now().date():
        errors['start_date'] = "Start date cannot be in the past."

    if errors:
        raise ValidationError(errors)