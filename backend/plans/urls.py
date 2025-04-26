from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    path('create/', views.PaymentPlanCreateView.as_view(), name='create-payment-plan'),
]