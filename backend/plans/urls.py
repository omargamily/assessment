from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    path('create/', views.PaymentPlanCreateView.as_view(), name='create-payment-plan'),
    path('', views.PaymentPlanListView.as_view(), name='list-payment-plans'),
    path('installments/<uuid:id>/pay/', views.InstallmentPayView.as_view(), name='pay-installment'),
]