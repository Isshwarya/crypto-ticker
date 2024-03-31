import numpy as np
from datetime import datetime
from statistics import median
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import CryptoPrice, LatestCryptoPrice, Settings
from .serializers import CryptoPriceSerializer, SettingsSerializer
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
        error_response = self._check_filter_correctness(request)
        if error_response:
            return error_response
        response = super(CryptoPriceListAPIView, self).list(
            request, *args, **kwargs)
        return response

    @staticmethod
    def _check_filter_correctness(request):
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
        start_dt = None
        end_dt = None
        data_collection_start_date = Settings.objects.get(
            name="data_collection_start_date").value
        if start:
            start_dt = datetime.strptime(
                start, '%Y-%m-%dT%H:%M:%S')
            data_collection_start_date_dt = datetime.strptime(
                data_collection_start_date, '%Y-%m-%d %H:%M:%S')
            if start_dt < data_collection_start_date_dt:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "detail": f"Data collection started from {data_collection_start_date_dt}, "
                                  "but the specified start_datetime precedes that"
                    }
                )
        if end:
            end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
            now_dt = datetime.now()
            if end_dt >= now_dt:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "detail": f"The specified end_datetime {end_dt} "
                                  f"must be lesser than current datetime {now_dt}"
                    }
                )

        if start and end:
            if start_dt > end_dt:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "detail": f"The specified end_datetime {end_dt} "
                                  f"fails to fall after the start_datetime {start_dt}"
                    }
                )


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
        error_response = self._check_filter_correctness(request)
        if error_response:
            return error_response
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        total_count = queryset.count()

        # No data indicates invalid input
        if not total_count:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "detail": "No matching data found"
                }
            )

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
