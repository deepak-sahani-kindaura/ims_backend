from utils.functions import get_uuid
from test_utils.tenant_user_base import TestCaseBase


class ProductTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/report/stock-summary"
        return super().setUp()

    @staticmethod
    def create_stock_data():
        """
        Helper method to create stock data for testing.
        """
        from stock.tests.test_stock import StockTestCase

        return StockTestCase().setUp().test_create_stock_out()

    def test_get_stock_summary(self):

        stock_data = self.create_stock_data()

        response = self.client.get(
            self.path, data={"product_id": stock_data["product_id"]}
        )

        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIsInstance(response_data["data"], list)
        self.assertEqual(len(response_data["data"]), 2)

        for item in response_data["data"]:
            self.assertIn("movement_type", item)
            self.assertIn("total_quantity", item)
            self.assertIsInstance(item["total_quantity"], int)
            self.assertIn(item["movement_type"], ["IN", "OUT"])

            product = item["product"]
            self.assertIsInstance(product, dict)
            self.assertIn("product_id", product)
            self.assertIn("product_name", product)
            self.assertIn("product_code", product)
            self.assertIn("category_id", product)
            self.assertIn("purchase_price", product)
            self.assertIn("sell_price", product)
            self.assertIsInstance(product["purchase_price"], float)
            self.assertIsInstance(product["sell_price"], float)

        return True

    def test_no_data_found(self):
        """
        Test case to check the response when no stock data is found.
        """
        self.client.get(self.path)

        response = self.client.get(self.path)

        self.data_not_found_404(response.json())

        return True

    def test_invalid_query_params(self):
        """
        Test case to check the response when invalid query parameters are provided.
        """
        response = self.client.get(self.path, {"product_id": get_uuid()})

        self.bad_request_404(response.json())

        response_data = response.json()

        self.assertIsInstance(response_data["errors"], list)
        self.assertEqual(len(response_data["errors"]), 1)

        error = response_data["errors"][0]
        self.assertEqual(error["code"], "NO_DATA_FOUND")
        self.assertEqual(error["message"], "No Data Found.")
        self.assertEqual(error["field"], "product_id")

        return True
