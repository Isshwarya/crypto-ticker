# from deepdiff import DeepDiff
from django.test import TestCase
from django.urls import reverse

from .models import CryptoPrice, LatestCryptoPrice, Settings


class CryptoTickerTestCase(TestCase):

    current_crypto_price = reverse("current-crypto-price")
    crypto_price_list = reverse("crypto-price-list")
    crypto_price_statistics = reverse("crypto-price-statistics")

    def test_current_crypto_price(self):
        response = (self.client.get(
            self.current_crypto_price, {"symbol": "BTCUSDT"}))
        assert response.status_code == 200
        data = response.json()
        assert "latest_price" in data
        assert "datetime" in data

    # def test_report_view_after_posting_transactions(self):
    #     with open('summer-break/data.csv') as fp:
    #         response = (self.client.post(
    #             self.store_transactions_url, {'data': fp}))
    #     assert response.status_code == 200
    #     assert str(response.content, 'utf-8') == ""
    #     response = self.client.get(self.report_url)
    #     expected_output = {
    #         "gross-revenue": 225.0, "expenses": 72.93, "net-revenue": 152.07
    #     }
    #     assert DeepDiff(expected_output, response.json()) == {}
    #     assert response.status_code == 200

    # def test_negative_transactions_store_view(self):
    #     with open('summer-break/incorrect_data.csv') as fp:
    #         response = (self.client.post(
    #             self.store_transactions_url, {'data': fp}))
    #     expected_output = \
    #         {"detail": "Failed while parsing csv file. Please ensure the "
    #                    "format is as given in the documentation"}
    #     assert response.status_code == 400
    #     assert DeepDiff(expected_output, response.json()) == {}

    # def test_delete_all_transactions(self):
    #     with open('summer-break/data.csv') as fp:
    #         response = (self.client.post(
    #             self.store_transactions_url, {'data': fp}))
    #     assert response.status_code == 200
    #     assert str(response.content, 'utf-8') == ""
    #     response = self.client.delete(self.store_transactions_url)
    #     assert response.status_code == 200
    #     self.test_report_view_without_any_transactions()
