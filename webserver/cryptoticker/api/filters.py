import django_filters
from .models import CryptoPrice


class CryptoPriceFilter(django_filters.FilterSet):
    start_datetime = django_filters.DateTimeFilter(
        field_name='datetime', lookup_expr='gte')
    end_datetime = django_filters.DateTimeFilter(
        field_name='datetime', lookup_expr='lte')
    symbol = django_filters.CharFilter(
        field_name='symbol', lookup_expr='exact')

    class Meta:
        model = CryptoPrice
        fields = ['start_datetime', 'end_datetime', 'symbol']
