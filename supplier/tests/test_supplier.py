from utils.functions import get_uuid
from test_utils.tenant_user_base import TestCaseBase


class SupplierTestCase(TestCaseBase):

    def setUp(self):
        self.path = "/api/supplier"
        self.path_id = "/api/supplier/{supplier_id}"
        return super().setUp()

    @staticmethod
    def get_supplier_data():
        return {
            "supplier_name": "Test Supplier",
            "supplier_code": "TEST_SUPPLIER",
        }

    def test_create_supplier(self):
        """
        Test creating a supplier
        """
        response = self.client.post(self.path, self.get_supplier_data())
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(response_data["data"]["supplier_code"], "TEST_SUPPLIER")
        self.assertEqual(response_data["data"]["supplier_name"], "Test Supplier")
        self.assertIn("supplier_id", response_data["data"])

        return response_data["data"]

    def test_already_exist_supplier(self):
        """
        Test creating a supplier that already exists
        """
        self.test_create_supplier()

        response = self.client.post(self.path, self.get_supplier_data())
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "supplier_code")
        self.assertEqual(response_data["errors"][0]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][0]["message"], "Already Exist.")

        self.assertEqual(response_data["errors"][1]["field"], "supplier_name")
        self.assertEqual(response_data["errors"][1]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][1]["message"], "Already Exist.")

        return True

    def test_create_supplier_with_invalid_data(self):
        """
        Test creating a supplier with invalid data
        """
        response = self.client.post(self.path, {})
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "supplier_code")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "supplier_name")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    def test_get_supplier(self):
        """
        Test getting a supplier
        """
        supplier_data = self.test_create_supplier()

        response = self.client.get(
            self.path_id.format(supplier_id=supplier_data["supplier_id"])
        )
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertEqual(response_data["data"]["supplier_code"], "TEST_SUPPLIER")
        self.assertEqual(response_data["data"]["supplier_name"], "Test Supplier")
        self.assertEqual(
            response_data["data"]["supplier_id"], supplier_data["supplier_id"]
        )

        return response_data["data"]

    def test_get_supplier_not_found(self):
        """
        Test getting a supplier that does not exist
        """
        response = self.client.get(self.path_id.format(supplier_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_get_supplier_list(self):
        """
        Test getting the list of suppliers
        """
        self.test_create_supplier()

        response = self.client.get(self.path)
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("list", response_data["data"])
        self.assertIn("pagination", response_data["data"])
        self.assertEqual(len(response_data["data"]["list"]), 1)

        supplier = response_data["data"]["list"][0]
        self.assertEqual(supplier["supplier_code"], "TEST_SUPPLIER")
        self.assertEqual(supplier["supplier_name"], "Test Supplier")
        self.assertIn("supplier_id", supplier)

        pagination = response_data["data"]["pagination"]
        self.assertEqual(pagination["count"], 1)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["current_page"], 1)
        self.assertEqual(pagination["total_pages"], 1)

        return True

    def test_no_data_found_supplier_list(self):
        """
        Test getting the list of suppliers when no data exists
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    @staticmethod
    def get_update_supplier_data():
        return {
            "supplier_name": "Updated Supplier",
            "supplier_code": "UPDATED_SUPPLIER",
        }

    def test_update_supplier(self):
        """
        Test updating a supplier
        """
        supplier_data = self.test_create_supplier()

        response = self.client.put(
            self.path_id.format(supplier_id=supplier_data["supplier_id"]),
            self.get_update_supplier_data(),
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)

        self.assertEqual(response_data["data"]["supplier_code"], "UPDATED_SUPPLIER")
        self.assertEqual(response_data["data"]["supplier_name"], "Updated Supplier")
        self.assertEqual(
            response_data["data"]["supplier_id"], supplier_data["supplier_id"]
        )

        return response_data["data"]

    def test_update_supplier_not_found(self):
        """
        Test updating a supplier that does not exist
        """
        response = self.client.put(
            self.path_id.format(supplier_id=get_uuid()),
            self.get_update_supplier_data(),
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_update_supplier_with_invalid_data(self):
        """
        Test updating a supplier with invalid data
        """
        supplier_data = self.test_create_supplier()

        response = self.client.put(
            self.path_id.format(supplier_id=supplier_data["supplier_id"]), {}
        )
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "supplier_code")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "supplier_name")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    @staticmethod
    def get_patch_data():
        return {
            "supplier_name": "Partially Updated Supplier",
        }

    def test_patch_supplier(self):
        """
        Test patching a supplier
        """
        supplier_data = self.test_create_supplier()
        response = self.client.patch(
            self.path_id.format(supplier_id=supplier_data["supplier_id"]),
            data=self.get_patch_data(),
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)
        self.assertEqual(response_data["data"]["supplier_code"], "TEST_SUPPLIER")
        self.assertEqual(
            response_data["data"]["supplier_name"], "Partially Updated Supplier"
        )
        self.assertEqual(
            response_data["data"]["supplier_id"], supplier_data["supplier_id"]
        )

        return True

    def test_patch_supplier_not_found(self):
        """
        Test patching a supplier that does not exist
        """
        response = self.client.patch(
            self.path_id.format(supplier_id=get_uuid()),
            data=self.get_patch_data(),
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_patch_supplier_with_no_data(self):
        """
        Test patching a supplier with no data
        """
        supplier_data = self.test_create_supplier()

        response = self.client.patch(
            self.path_id.format(supplier_id=supplier_data["supplier_id"]), {}
        )
        response_data = response.json()

        self.patch_data_not_provided_400(response_data)

        return True

    def test_delete_supplier(self):
        """
        Test deleting a supplier
        """
        supplier_data = self.test_create_supplier()

        response = self.client.delete(
            self.path_id.format(supplier_id=supplier_data["supplier_id"])
        )

        self.delete_success_204(response.status_code)

        return True

    def test_delete_supplier_not_found(self):
        """
        Test deleting a supplier that does not exist
        """
        response = self.client.delete(self.path_id.format(supplier_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
