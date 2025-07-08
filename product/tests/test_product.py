from utils.functions import get_uuid
from test_utils.tenant_user_base import TestCaseBase


class ProductTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/product"
        self.path_id = "/api/product/{product_id}"
        return super().setUp()

    @staticmethod
    def get_category_data():
        """
        Helper method to create a category for product testing
        """
        from category.tests.test_category import CategoryTestCase

        return CategoryTestCase().setUp().test_create_category()

    @staticmethod
    def get_product_data():

        return {
            "product_name": "Test Product",
            "product_code": "TEST_Product:001",
            "sell_price": 30000,
            "purchase_price": 25000,
        }

    def test_create_product(self):
        """
        Test creating a product
        """

        data = self.get_product_data()
        data["category_id"] = self.get_category_data()["category_id"]

        response = self.client.post(self.path, data)
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(response_data["data"]["product_code"], "TEST_Product:001")
        self.assertEqual(response_data["data"]["product_name"], "Test Product")
        self.assertEqual(response_data["data"]["sell_price"], 30000.0)
        self.assertEqual(response_data["data"]["purchase_price"], 25000.0)
        self.assertEqual(response_data["data"]["category_id"], data["category_id"])
        self.assertIn("product_id", response_data["data"])

        return response_data["data"]

    def test_create_product_already_exists(self):
        """
        Test creating a product that already exists
        """
        already_existing_product = self.test_create_product()

        data = self.get_product_data()

        data["category_id"] = already_existing_product["category_id"]

        response = self.client.post(self.path, data=data)
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "product_code")
        self.assertEqual(response_data["errors"][0]["code"], "DUPLICATE_ENTRY")

        self.assertEqual(response_data["errors"][1]["field"], "product_name")
        self.assertEqual(response_data["errors"][1]["code"], "DUPLICATE_ENTRY")

        return True

    def test_create_product_invalid_category(self):
        """
        Test creating a product with an invalid category
        """
        data = self.get_product_data()
        data["category_id"] = get_uuid()
        response = self.client.post(self.path, data)
        response_data = response.json()
        self.bad_request_404(response_data)
        self.assertEqual(len(response_data["errors"]), 1)
        self.assertEqual(response_data["errors"][0]["field"], "category_id")
        self.assertEqual(response_data["errors"][0]["code"], "NO_DATA_FOUND")
        self.assertEqual(response_data["errors"][0]["message"], "No Data Found.")

        return True

    def test_create_product_invalid_data(self):
        """
        Test creating a product with missing data
        """
        response = self.client.post(self.path, {})
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 5)

        self.assertEqual(response_data["errors"][0]["field"], "category_id")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "product_code")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][2]["field"], "product_name")
        self.assertEqual(response_data["errors"][2]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][2]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][3]["field"], "sell_price")
        self.assertEqual(response_data["errors"][3]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][3]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][4]["field"], "purchase_price")
        self.assertEqual(response_data["errors"][4]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][4]["message"], "This field is required."
        )

        return True

    def test_get_product(self):
        """
        Test fetching a single product
        """
        product = self.test_create_product()

        response = self.client.get(
            self.path_id.format(product_id=product["product_id"])
        )
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("product_id", response_data["data"])
        self.assertIn("category_id", response_data["data"])
        self.assertEqual(response_data["data"]["product_code"], "TEST_Product:001")
        self.assertEqual(response_data["data"]["product_name"], "Test Product")
        self.assertEqual(response_data["data"]["sell_price"], 30000.0)
        self.assertEqual(response_data["data"]["purchase_price"], 25000.0)

        return True

    def test_get_product_not_found(self):
        """
        Test getting a product that does not exist
        """
        response = self.client.get(self.path_id.format(product_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_get_product_list(self):
        """
        Test getting list of products
        """
        self.test_create_product()

        response = self.client.get(self.path)
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertEqual(len(response_data["data"]["list"]), 1)
        product = response_data["data"]["list"][0]

        self.assertIn("product_id", product)
        self.assertEqual(product["product_name"], "Test Product")
        self.assertEqual(product["product_code"], "TEST_Product:001")

        return True

    def test_no_data_found_product_list(self):
        """
        Test product list when no data exists
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    @staticmethod
    def get_update_product_data():
        """
        Helper method to get data for updating a product
        """
        return {
            "product_name": "Updated Product",
            "product_code": "UPDATED:001",
            "sell_price": 50000,
            "purchase_price": 45000,
        }

    def test_update_product(self):
        """
        Test updating product
        """
        product = self.test_create_product()
        data = self.get_update_product_data()
        data["category_id"] = product["category_id"]

        response = self.client.put(
            self.path_id.format(product_id=product["product_id"]),
            data,
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)

        self.assertIn("product_id", response_data["data"])
        self.assertIn("category_id", response_data["data"])
        self.assertEqual(response_data["data"]["product_code"], "UPDATED:001")
        self.assertEqual(response_data["data"]["product_name"], "Updated Product")
        self.assertEqual(response_data["data"]["sell_price"], 50000.0)
        self.assertEqual(response_data["data"]["purchase_price"], 45000.0)

        return True

    def test_update_product_not_found(self):
        """
        Test updating a non-existent product
        """
        response = self.client.put(
            self.path_id.format(product_id=get_uuid()),
            self.get_update_product_data(),
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_update_product_invalid_data(self):
        """
        Test updating product with missing data
        """
        product = self.test_create_product()

        response = self.client.put(
            self.path_id.format(product_id=product["product_id"]),
            {},
        )
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(response_data["errors"][0]["field"], "category_id")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "product_code")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][2]["field"], "product_name")
        self.assertEqual(response_data["errors"][2]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][2]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][3]["field"], "sell_price")
        self.assertEqual(response_data["errors"][3]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][3]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][4]["field"], "purchase_price")
        self.assertEqual(response_data["errors"][4]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][4]["message"], "This field is required."
        )

        return True

    @staticmethod
    def get_patch_data():
        return {"product_name": "Patched Product"}

    def test_patch_product(self):
        """
        Test partially updating a product
        """
        product = self.test_create_product()

        response = self.client.patch(
            self.path_id.format(product_id=product["product_id"]),
            self.get_patch_data(),
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)
        self.assertEqual(response_data["data"]["product_name"], "Patched Product")

        return True

    def test_patch_product_not_found(self):
        """
        Test patching a product that doesn't exist
        """
        response = self.client.patch(
            self.path_id.format(product_id=get_uuid()),
            self.get_patch_data(),
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_patch_product_no_data(self):
        """
        Test patching a product with empty body
        """
        product = self.test_create_product()

        response = self.client.patch(
            self.path_id.format(product_id=product["product_id"]),
            {},
        )
        response_data = response.json()

        self.patch_data_not_provided_400(response_data)

        return True

    def test_delete_product(self):
        """
        Test deleting a product
        """
        product = self.test_create_product()

        response = self.client.delete(
            self.path_id.format(product_id=product["product_id"])
        )

        self.delete_success_204(response.status_code)

        return True

    def test_delete_product_not_found(self):
        """
        Test deleting a product that doesn't exist
        """
        response = self.client.delete(self.path_id.format(product_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
