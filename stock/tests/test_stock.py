from utils.functions import get_uuid
from test_utils.tenant_user_base import TestCaseBase


class StockTestCase(TestCaseBase):
    def setUp(self):
        self.path = "/api/stock"
        self.path_id = "/api/stock/{stock_id}"
        return super().setUp()

    @staticmethod
    def get_product_data():
        """
        Helper method to create a product for stock testing
        """
        from product.tests.test_product import ProductTestCase

        return ProductTestCase().setUp().test_create_product()

    @staticmethod
    def get_supplier_data():
        """
        Helper method to create a supplier for stock testing
        """
        from supplier.tests.test_supplier import SupplierTestCase

        return SupplierTestCase().setUp().test_create_supplier()

    @staticmethod
    def get_stock_data():

        return {
            "price": 32,
            "quantity": 20,
            "movement_type": "IN",
            "reference_number": "IN:2F54D807",
        }

    def test_create_stock_in(self):
        """
        Test creating a stock entry with movement type IN
        """
        data = self.get_stock_data()

        product = self.get_product_data()
        supplier = self.get_supplier_data()

        data["product_id"] = product["product_id"]
        data["supplier_id"] = supplier["supplier_id"]

        response = self.client.post(self.path, data)
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(response_data["data"]["movement_type"], "IN")
        self.assertEqual(response_data["data"]["price"], 32.0)
        self.assertEqual(response_data["data"]["quantity"], 20)
        self.assertEqual(response_data["data"]["product_id"], data["product_id"])
        self.assertEqual(response_data["data"]["supplier_id"], data["supplier_id"])
        self.assertIn("stock_id", response_data["data"])

        return response_data["data"]

    @staticmethod
    def get_stock_data_out():
        return {
            "price": 32,
            "quantity": 10,
            "movement_type": "OUT",
            "reference_number": "OUT:2F54D807",
        }

    def test_create_stock_out(self):
        """
        Test creating a stock entry with movement type IN
        """

        stock_in = self.test_create_stock_in()

        data = self.get_stock_data_out()

        data["product_id"] = stock_in["product_id"]
        data["supplier_id"] = stock_in["supplier_id"]

        response = self.client.post(self.path, data)
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(response_data["data"]["movement_type"], "OUT")
        self.assertEqual(response_data["data"]["price"], 32.0)
        self.assertEqual(response_data["data"]["quantity"], 10)
        self.assertEqual(response_data["data"]["product_id"], data["product_id"])
        self.assertEqual(response_data["data"]["supplier_id"], data["supplier_id"])
        self.assertIn("stock_id", response_data["data"])

        return response_data["data"]

    def test_create_stock_in_missing_supplier_and_product(self):
        """
        Test creating a stock IN without supplier (should fail)
        """
        data = self.get_stock_data()
        data["product_id"] = get_uuid()
        data["supplier_id"] = get_uuid()

        response = self.client.post(self.path, data)
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "product_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")

        self.assertEqual(response_data["errors"][1]["field"], "supplier_id")
        self.assertEqual(response_data["errors"][1]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][1]["message"], "No Data Found.")

        return True

    @staticmethod
    def invalid_data():
        return {
            "price": "asd",
            "quantity": "",
            "movement_type": "OUTY",
            "reference_number": 234.324,
            "product_id": "invalid-uuid",
            "supplier_id": "invalid-uuid",
        }

    def test_create_stock_invalid_data(self):
        """
        Test creating a stock entry with missing fields
        """
        response = self.client.post(self.path, self.invalid_data())
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 5)

        self.assertEqual(response_data["errors"][0]["field"], "product_id")
        self.assertEqual(response_data["errors"][0]["code"], "INVALID")
        self.assertEqual(response_data["errors"][0]["message"], "Must be a valid UUID.")

        self.assertEqual(response_data["errors"][1]["field"], "supplier_id")
        self.assertEqual(response_data["errors"][1]["code"], "INVALID")
        self.assertEqual(response_data["errors"][1]["message"], "Must be a valid UUID.")

        self.assertEqual(response_data["errors"][2]["field"], "price")
        self.assertEqual(response_data["errors"][2]["code"], "INVALID")
        self.assertEqual(
            response_data["errors"][2]["message"], "A valid number is required."
        )

        self.assertEqual(response_data["errors"][3]["field"], "movement_type")
        self.assertEqual(response_data["errors"][3]["code"], "INVALID_CHOICE")
        self.assertEqual(
            response_data["errors"][3]["message"], '"OUTY" is not a valid choice.'
        )

        self.assertEqual(response_data["errors"][4]["field"], "quantity")
        self.assertEqual(response_data["errors"][4]["code"], "INVALID")
        self.assertEqual(
            response_data["errors"][4]["message"], "A valid integer is required."
        )

        return True

    @staticmethod
    def max_limit_out_stock_data():
        return {
            "price": 32,
            "quantity": 1000000,
            "movement_type": "OUT",
            "reference_number": "OUT:2F54D807",
        }

    def test_create_stock_in_invalid_movement_type_out(self):

        stock_in = self.test_create_stock_in()

        data = self.max_limit_out_stock_data()

        data["product_id"] = stock_in["product_id"]
        data["supplier_id"] = stock_in["supplier_id"]

        response = self.client.post(self.path, data)
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "quantity")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(
            response_data["errors"][0]["message"],
            "The requested stock quantity is not available.",
        )
        return True

    def test_create_supplier_required_for_stock_in(self):
        """
        Test creating a stock IN without supplier (should fail)
        """
        data = self.get_stock_data()
        data["product_id"] = self.get_product_data()["product_id"]
        data["supplier_id"] = None
        response = self.client.post(self.path, data)
        response_data = response.json()
        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "supplier_id")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )
        return True

    def test_get_stock(self):
        """
        Test retrieving a stock entry by ID
        """
        stock = self.test_create_stock_in()

        response = self.client.get(self.path_id.format(stock_id=stock["stock_id"]))
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("stock_id", response_data["data"])
        self.assertEqual(response_data["data"]["movement_type"], "IN")
        self.assertEqual(response_data["data"]["quantity"], 20)
        self.assertEqual(response_data["data"]["price"], 32.0)
        self.assertIn("reference_number", response_data["data"])

        return True

    def test_get_stock_not_found(self):
        """
        Test retrieving a non-existent stock entry
        """
        response = self.client.get(self.path_id.format(stock_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_get_stock_list(self):
        """
        Test retrieving a list of stock entries
        """
        self.test_create_stock_in()

        response = self.client.get(self.path)
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("list", response_data["data"])
        self.assertIn("pagination", response_data["data"])

        self.assertEqual(len(response_data["data"]["list"]), 1)

        stock = response_data["data"]["list"][0]
        self.assertIn("stock_id", stock)
        self.assertEqual(stock["movement_type"], "IN")
        self.assertEqual(stock["quantity"], 20)
        self.assertEqual(stock["price"], 32.0)
        self.assertIn("reference_number", stock)
        self.assertIn("product_id", stock)
        self.assertIn("supplier_id", stock)

        pagination = response_data["data"]["pagination"]
        self.assertEqual(pagination["count"], 1)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["current_page"], 1)
        self.assertEqual(pagination["total_pages"], 1)

        return True

    def test_no_data_found_stock_list(self):
        """
        Test retrieving stock list when there is no data
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_delete_stock(self):
        """
        Test deleting a stock entry
        """
        stock = self.test_create_stock_in()

        response = self.client.delete(self.path_id.format(stock_id=stock["stock_id"]))
        self.delete_success_204(response.status_code)

        return True

    def test_delete_stock_not_found(self):
        """
        Test deleting a non-existent stock entry
        """
        response = self.client.delete(self.path_id.format(stock_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
