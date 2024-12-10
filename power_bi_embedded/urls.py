from django.urls import path
from .views import power_bi_view, power_bi_view_url, proxy_view

urlpatterns = [
    path('', power_bi_view, name='power_bi'),
    path('url', power_bi_view_url, name='power_bi_view_url'),
    path('proxy', proxy_view, name='power_bi_view_proxy'),
]
