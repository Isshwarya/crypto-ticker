from django.urls import path
from .views import LatestCryptoPriceView, CryptoPriceListAPIView, CryptoPriceStatisticsAPIView

urlpatterns = [
    path('current_price/', LatestCryptoPriceView.as_view(),
         name="current-crypto-price"),
    path('crypto_price/', CryptoPriceListAPIView.as_view(),
         name='crypto-price-list'),
    path('crypto_price/statistics/', CryptoPriceStatisticsAPIView.as_view(),
         name='crypto-price-statistics'),
]
