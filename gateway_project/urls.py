from .views import *
from django.urls import path



url_patterns = [
    path('deposit/', Deposit.as_view(), name="deposit-page")
]