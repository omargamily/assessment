import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class PaymentPlan(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Paid', 'Paid'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='merchant_plans',
        limit_choices_to={'role': 'merchant'}
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_plans',
        limit_choices_to={'role': 'user'}
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.IntegerField()
    start_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_email = self.user.email if self.user else 'N/A'
        return f'Plan for {user_email} by Merchant {self.merchant.email} - Amount: {self.total_amount}'