# plans/services.py
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from django.db import transaction
from .models import PaymentPlan, Installment
from django.contrib.auth import get_user_model
from .validators import validate_plan_creation_data
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def _calculate_installments(plan: PaymentPlan):
    """
    Calculates and creates installments for a given payment plan.
    This function assumes the plan object is already saved.
    """
    installments_to_create = []
    installment_amount = (plan.total_amount / plan.number_of_installments).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Last installment will include the remaining amount to make sure installments have a fixed sum
    total_calculated = installment_amount * (plan.number_of_installments - 1)
    last_installment_amount = plan.total_amount - total_calculated

    for i in range(plan.number_of_installments):
        due_date = plan.start_date + relativedelta(months=i)
        # Use last installment amount for the final payment, regular amount for others ( if last installment )
        if i == plan.number_of_installments - 1:
            amount = last_installment_amount
        else:
            amount = installment_amount
        installments_to_create.append(
            Installment(
                plan=plan,
                due_date=due_date,
                amount=amount,
                status='Pending'
            )
        )
    
    return installments_to_create


@transaction.atomic
def create_payment_plan(merchant: User, user: User, total_amount: Decimal, number_of_installments: int, start_date) -> PaymentPlan:
    """
    Creates a PaymentPlan and its associated Installments.
    """
    validate_plan_creation_data(total_amount, number_of_installments, start_date)
    
    plan = PaymentPlan.objects.create(
        merchant=merchant,
        user=user,
        total_amount=total_amount,
        number_of_installments=number_of_installments,
        start_date=start_date
    )

    # Calculate installments using the helper function
    installments = _calculate_installments(plan)
    
    # Bulk create the calculated installments
    if installments:
        Installment.objects.bulk_create(installments)

    return plan


def update_installment_statuses():
    """
    Updates the status of installments based on their due dates.
    - Sets status to 'Due' if the due date is today
    - Sets status to 'Late' if the due date has passed
    Returns the number of installments updated.
    """
    today = timezone.now().date()
    
    # Update installments that are due today to 'Due' status
    due_today_count = Installment.objects.filter(
        due_date=today,
        status='Pending'
    ).update(status='Due')
    
    # Update overdue installments to 'Late' status
    overdue_count = Installment.objects.filter(
        due_date__lt=today,
        status__in=['Pending', 'Due']
    ).update(status='Late')
    
    return due_today_count + overdue_count


def check_upcoming_installments():
    """
    Checks for installments that are due in 3 days.
    Returns a list of upcoming installments.
    """
    future_date = timezone.now().date() + timedelta(days=3)
    
    upcoming_installments = Installment.objects.filter(
        due_date=future_date,
        status='Pending'
    ).select_related('plan__user', 'plan__merchant')
    
    return upcoming_installments