from utils.functions import get_uuid
from test_utils.tenant_user_base import TestCaseBase


class CategoryTestCase(TestCaseBase):

    def setUp(self):

        self.path = "/api/category"
        self.path_id = "/api/category/{category_id}"

        return super().setUp()

    @staticmethod
    def get_category_data():
        return {
            "category_name": "Test Category",
            "category_code": "TEST_CATEGORY",
        }

    def test_create_category(self):
        """
        Test creating a category
        """
        response = self.client.post(self.path, self.get_category_data())
        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertEqual(response_data["data"]["category_code"], "TEST_CATEGORY")
        self.assertEqual(response_data["data"]["category_name"], "Test Category")
        self.assertIn("category_id", response_data["data"])

        return response_data["data"]

    def test_already_exist_category(self):
        """
        Test creating a category that already exists
        """
        self.test_create_category()

        response = self.client.post(self.path, self.get_category_data())
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "category_code")
        self.assertEqual(response_data["errors"][0]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][0]["message"], "Already Exist.")

        self.assertEqual(response_data["errors"][1]["field"], "category_name")
        self.assertEqual(response_data["errors"][1]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][1]["message"], "Already Exist.")

        return True

    def test_create_category_with_invalid_data(self):
        """
        Test creating a category with invalid data
        """
        response = self.client.post(self.path, {})
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "category_code")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "category_name")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    def test_get_category(self):
        """
        Test getting a category
        """
        category_data = self.test_create_category()

        response = self.client.get(
            self.path_id.format(category_id=category_data["category_id"])
        )
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertEqual(response_data["data"]["category_code"], "TEST_CATEGORY")
        self.assertEqual(response_data["data"]["category_name"], "Test Category")
        self.assertEqual(
            response_data["data"]["category_id"], category_data["category_id"]
        )

        return response_data["data"]

    def test_get_category_not_found(self):
        """
        Test getting a category that does not exist
        """
        response = self.client.get(self.path_id.format(category_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_get_category_list(self):
        """
        Test getting the list of categories
        """
        self.test_create_category()

        response = self.client.get(self.path)
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("list", response_data["data"])
        self.assertIn("pagination", response_data["data"])
        self.assertEqual(len(response_data["data"]["list"]), 1)

        category = response_data["data"]["list"][0]
        self.assertEqual(category["category_code"], "TEST_CATEGORY")
        self.assertEqual(category["category_name"], "Test Category")
        self.assertIn("category_id", category)

        pagination = response_data["data"]["pagination"]
        self.assertEqual(pagination["count"], 1)
        self.assertEqual(pagination["page_size"], 10)
        self.assertEqual(pagination["current_page"], 1)
        self.assertEqual(pagination["total_pages"], 1)

        return True

    def test_no_data_found_category_list(self):
        """
        Test getting the list of categories when no data exists
        """
        response = self.client.get(self.path)
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    @staticmethod
    def get_update_category_data():
        return {
            "category_name": "Updated Category",
            "category_code": "UPDATED_CATEGORY",
        }

    def test_update_category(self):
        """
        Test updating a category
        """
        category_data = self.test_create_category()

        response = self.client.put(
            self.path_id.format(category_id=category_data["category_id"]),
            self.get_update_category_data(),
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)

        self.assertEqual(response_data["data"]["category_code"], "UPDATED_CATEGORY")
        self.assertEqual(response_data["data"]["category_name"], "Updated Category")
        self.assertEqual(
            response_data["data"]["category_id"], category_data["category_id"]
        )

        return response_data["data"]

    def test_update_category_not_found(self):
        """
        Test updating a category that does not exist
        """
        response = self.client.put(
            self.path_id.format(category_id=get_uuid()),
            self.get_update_category_data(),
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_update_category_with_invalid_data(self):
        """
        Test updating a category with invalid data
        """
        category_data = self.test_create_category()

        response = self.client.put(
            self.path_id.format(category_id=category_data["category_id"]), {}
        )
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "category_code")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "category_name")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    @staticmethod
    def get_patch_data():
        return {
            "category_name": "Partially Updated Category",
        }

    def test_patch_category(self):
        """
        Test patching a category
        """
        category_data = self.test_create_category()
        response = self.client.patch(
            self.path_id.format(category_id=category_data["category_id"]),
            data=self.get_patch_data(),
        )
        response_data = response.json()
        self.update_success_ok_200(response_data)
        self.assertEqual(response_data["data"]["category_code"], "TEST_CATEGORY")
        self.assertEqual(
            response_data["data"]["category_name"], "Partially Updated Category"
        )
        self.assertEqual(
            response_data["data"]["category_id"], category_data["category_id"]
        )

        return True

    def test_patch_category_not_found(self):
        """
        Test patching a category that does not exist
        """
        response = self.client.patch(
            self.path_id.format(category_id=get_uuid()),
            data=self.get_patch_data(),
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_patch_category_with_no_data(self):
        """
        Test patching a category with no data
        """
        category_data = self.test_create_category()

        response = self.client.patch(
            self.path_id.format(category_id=category_data["category_id"]), {}
        )
        response_data = response.json()

        self.patch_data_not_provided_400(response_data)

        return True

    def test_delete_category(self):
        """
        Test deleting a category
        """
        category_data = self.test_create_category()

        response = self.client.delete(
            self.path_id.format(category_id=category_data["category_id"])
        )

        self.delete_success_204(response.status_code)

        return True

    def test_delete_category_not_found(self):
        """
        Test deleting a category that does not exist
        """
        response = self.client.delete(self.path_id.format(category_id=get_uuid()))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
