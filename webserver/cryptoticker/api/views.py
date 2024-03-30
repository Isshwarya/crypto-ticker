from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import CryptoPrice, LatestCryptoPrice


class LatestCryptoPriceView(APIView):
    """
    This view helps to retrieve latest price of the given cryptocurrency pair.
    """

    def get(self, request):
        symbol = request.query_params.get('symbol')
        queryset = LatestCryptoPrice.objects.filter(symbol=symbol)
        return Response({"latest_price": queryset[0].price})


