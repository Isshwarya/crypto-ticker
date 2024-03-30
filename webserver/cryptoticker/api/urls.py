from django.urls import path
from .views import LatestCryptoPriceView

urlpatterns = [
   path('current_price/', LatestCryptoPriceView.as_view(),
        name="current_crypto_price"),
]
