from rest_framework import serializers
from .models import CryptoPrice, LatestCryptoPrice


class CryptoPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CryptoPrice
        fields = '__all__'


class LatestCryptoPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = LatestCryptoPrice
        fields = '__all__'
