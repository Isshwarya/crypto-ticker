import numpy as np
from statistics import median
from rest_framework import generics, status
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
        if not queryset.count():
            # Provided symbol is invalid or not supported yet
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": f"The given cryptocurrency pair {symbol} is "
                              "either not supported or invalid"
                }
            )
        else:
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

    def list(self, request, *args, **kwargs):
        response = super(CryptoPriceListAPIView, self).list(
            request, *args, **kwargs)
        if not response.data.get("count"):
            return self._check_filter_correctness(request)
        else:
            return response

    @staticmethod
    def _check_filter_correctness(cls, request):
        symbol = request.query_params.get('symbol')
        start = request.query_params.get('start_datetime')
        end = request.query_params.get('end_datetime')
        if symbol:
            supported_symbols = LatestCryptoPrice.objects.values_list(
                'symbol', flat=True)
            if symbol not in supported_symbols:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "detail": f"The given cryptocurrency pair {symbol} is "
                        "either not supported or invalid"
                    }
                )
        if start:
            pass


class CryptoPriceStatisticsAPIView(CryptoPriceListAPIView):
    def list(self, request, *args, **kwargs):
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": "symbol is a mandatory query param"
                }
            )
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        total_count = queryset.count()

        # No data indicates invalid input
        if not total_count:
            return self._check_filter_correctness(request)

        # Calculate additional statistics
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
