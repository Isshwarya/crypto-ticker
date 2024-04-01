import re
from deepdiff import DeepDiff
from pprint import pformat
from django.apps import apps
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta

from .models import CryptoPrice, LatestCryptoPrice, Settings


class CryptoTickerTestCase(TestCase):

    current_crypto_price = reverse("current-crypto-price")
    crypto_price_list = reverse("crypto-price-list")
    crypto_price_statistics = reverse("crypto-price-statistics")

    def setUp(self):
        super(CryptoTickerTestCase, self).setUp()

        with connection.schema_editor() as schema_editor:
            get_models = apps.get_models
            self.unmanaged_models = [
                m for m in get_models() if not m._meta.managed]
            for m in self.unmanaged_models:
                schema_editor.create_model(m)

        # Supporting data
        self.data_collection_start_date = datetime.strptime(
            "2024-04-01T11:02:47", '%Y-%m-%dT%H:%M:%S')
        self.min_4 = datetime.strptime(
            "2024-04-01T11:03:47", '%Y-%m-%dT%H:%M:%S')
        self.min_3 = datetime.strptime(
            "2024-04-01T11:04:47", '%Y-%m-%dT%H:%M:%S')
        self.min_2 = datetime.strptime(
            "2024-04-01T11:05:47", '%Y-%m-%dT%H:%M:%S')

        # Adding data

        LatestCryptoPrice(symbol="BTCUSDT", price="3333.33  ",
                          datetime=self.min_2).save()

        Settings(name="data_collection_start_date",
                 value=self.data_collection_start_date).save()

        CryptoPrice(symbol="BTCUSDT", price="1111.11",
                    datetime=self.min_4).save()
        CryptoPrice(symbol="BTCUSDT", price="2222.22",
                    datetime=self.min_3).save()
        CryptoPrice(symbol="BTCUSDT", price="3333.33",
                    datetime=self.min_2).save()

    def tearDown(self):
        super(CryptoTickerTestCase, self).tearDown()

        with connection.schema_editor() as schema_editor:
            get_models = apps.get_models
            self.unmanaged_models = [
                m for m in get_models() if not m._meta.managed]
            for m in self.unmanaged_models:
                schema_editor.delete_model(m)

    def test_current_crypto_price(self):
        response = (self.client.get(
            self.current_crypto_price, {"symbol": "BTCUSDT"}))
        assert response.status_code == 200
        data = response.json()
        assert data["latest_price"] == 3333.33, data["latest_price"]
        assert "datetime" in data

    def test_negative_current_crypto_price(self):
        response = (self.client.get(
            self.current_crypto_price, {"symbol": "JUNK"}))
        assert response.status_code == 400
        expected_output = {
            "detail": "The given cryptocurrency pair JUNK is either not supported or invalid"}
        assert DeepDiff(expected_output, response.json()
                        ) == {}, response.json()

    def test_list_price(self):
        response = (self.client.get(
            self.crypto_price_list, {"symbol": "BTCUSDT",
                                     "start_datetime": self.data_collection_start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                     "end_datetime": self.min_3.strftime('%Y-%m-%dT%H:%M:%S')}))
        assert response.status_code == 200
        expected_output = {'count': 2, 'next': None, 'previous': None, 'results': [
            {'id': 1, 'datetime': '2024-04-01T11:03:47', 'symbol': 'BTCUSDT', 'price': 1111.11}, {'id': 2, 'datetime': '2024-04-01T11:04:47', 'symbol': 'BTCUSDT', 'price': 2222.22}]}
        assert DeepDiff(expected_output, response.json()
                        ) == {}, response.json()

    def test_negative_1_list_price(self):
        response = (self.client.get(
            self.crypto_price_list, {"symbol": "JUNK",
                                     "start_datetime": self.data_collection_start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                     "end_datetime": self.min_3.strftime('%Y-%m-%dT%H:%M:%S')}))
        assert response.status_code == 400
        expected_output = {
            'detail': 'The given cryptocurrency pair JUNK is either not supported or invalid'}
        assert DeepDiff(expected_output, response.json()
                        ) == {}, response.json()

    def test_negative_2_list_price(self):
        response = (self.client.get(
            self.crypto_price_list, {"symbol": "BTCUSDT",
                                     "start_datetime": "2022-09-09T04:23:56",
                                     "end_datetime": self.min_3.strftime('%Y-%m-%dT%H:%M:%S')}))
        assert response.status_code == 400
        expected_output = {
            'detail': 'Data collection started from 2024-04-01 11:02:47, but the specified start_datetime precedes that'}
        assert DeepDiff(expected_output, response.json()
                        ) == {}, response.json()

    def test_negative_3_list_price(self):
        response = (self.client.get(
            self.crypto_price_list, {"symbol": "BTCUSDT",
                                     "start_datetime": self.min_3.strftime('%Y-%m-%dT%H:%M:%S'),
                                     "end_datetime": (datetime.now() + timedelta(minutes=4)).strftime('%Y-%m-%dT%H:%M:%S')}))
        assert response.status_code == 400, f"status code was {response.status_code}"
        data = response.json()
        assert re.search(
            "The specified end_datetime .+ must be lesser than current datetime .+", data["detail"]), pformat(data)

    def test_statistics(self):
        response = (self.client.get(
            self.crypto_price_statistics, {"symbol": "BTCUSDT",
                                           "start_datetime": self.data_collection_start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                           "end_datetime": self.min_3.strftime('%Y-%m-%dT%H:%M:%S')}))
        assert response.status_code == 200
        expected_output = {'crypto_prices': [{'id': 1, 'datetime': '2024-04-01T11:03:47', 'symbol': 'BTCUSDT', 'price': 1111.11}, {'id': 2, 'datetime': '2024-04-01T11:04:47',
                                                                                                                                   'symbol': 'BTCUSDT', 'price': 2222.22}], 'total_count': 2, 'average_price': 1666.665, 'median_price': 1666.665, 'standard_deviation': 555.555, 'percentage_change': 100.0}
        assert DeepDiff(expected_output, response.json()
                        ) == {}, response.json()

    def test_negative_1_statistics(self):
        response = (self.client.get(
            self.crypto_price_statistics, {
                "start_datetime": self.data_collection_start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                "end_datetime": self.min_3.strftime('%Y-%m-%dT%H:%M:%S')}))
        assert response.status_code == 400
        expected_output = {'detail': 'symbol is a mandatory query param'}
        assert DeepDiff(expected_output, response.json()
                        ) == {}, response.json()
