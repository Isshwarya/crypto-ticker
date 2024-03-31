import numpy as np
from statistics import median
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import CryptoPrice, LatestCryptoPrice
from .serializers import CryptoPriceSerializer
from .filters import CryptoPriceFilter


class LatestCryptoPriceView(APIView):
    """
    This view helps to retrieve latest price of the given cryptocurrency pair.
    """

    def get(self, request):
        symbol = request.query_params.get('symbol')
        queryset = LatestCryptoPrice.objects.filter(symbol=symbol)
        return Response(
            {
                "latest_price": queryset[0].price,
                "datetime": queryset[0].datetime
            })


class CryptoPriceListAPIView(generics.ListAPIView):
    queryset = CryptoPrice.objects.all()
    serializer_class = CryptoPriceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CryptoPriceFilter


class CryptoPriceStatisticsAPIView(CryptoPriceListAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Calculate additional statistics
        total_count = queryset.count()
        values = queryset.values_list('price', flat=True)
        average_price = np.average(values)
        median_price = np.median(values)
        standard_deviation = np.std(values)

        # Compute percentage change
        latest_price = queryset.latest('datetime').price
        earliest_price = queryset.earliest('datetime').price
        percentage_change = ((latest_price - earliest_price) /
                             earliest_price) * 100 if earliest_price != 0 else 0

        data = {
            'crypto_prices': serializer.data,
            'total_count': total_count,
            'average_price': average_price,
            'median_price': median_price,
            'standard_deviation': standard_deviation,
            'percentage_change': percentage_change
        }

        return Response(data)
