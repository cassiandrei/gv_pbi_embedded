from django.urls import path
from .views import power_bi_view

urlpatterns = [
    path('', power_bi_view, name='power_bi'),
]
