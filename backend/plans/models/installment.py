import uuid
from django.db import models
from .payment_plan import PaymentPlan

class Installment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Due', 'Due'),
        ('Paid', 'Paid'),
        ('Late', 'Late')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Installment for Plan {self.plan.id} - Due: {self.due_date} - Status: {self.status}'