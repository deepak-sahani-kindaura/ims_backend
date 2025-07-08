"""Test cases for tenant API including create, list, update, retrieve, and delete operations."""

from utils.functions import get_uuid

from test_utils.base_super_admin import TestCaseBase


def tenant_success_data():
    """Return valid data for creating a tenant."""
    return {"tenant_code": "test", "tenant_name": "Test Tenant"}


class TenantTestCase(TestCaseBase):
    """Test cases for tenant API including create, list, update, retrieve, and delete operations."""

    def setUp(self):
        """Set up test case with base tenant API path."""
        self.path = "/api/tenant"
        self.path_id = "/api/tenant/{tenant_id}"
        return super().setUp()

    def test_tenant_create(self, data=tenant_success_data()):
        """Test successful tenant creation."""
        response = self.client.post(self.path, data=data)

        response_data = response.json()

        self.created_successfully_201(response_data)

        self.assertIn("tenant_id", response_data["data"])
        self.assertEqual(response_data["data"]["tenant_code"], data["tenant_code"])
        self.assertEqual(response_data["data"]["tenant_name"], data["tenant_name"])

        return response_data["data"]

    def test_tenant_already_exist(self):
        """Test creating a tenant with existing code and name returns duplicate error."""
        self.test_tenant_create()

        data = tenant_success_data()
        response = self.client.post(self.path, data=data)
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "tenant_code")
        self.assertEqual(response_data["errors"][0]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][0]["message"], "Already Exist.")

        self.assertEqual(response_data["errors"][1]["field"], "tenant_name")
        self.assertEqual(response_data["errors"][1]["code"], "DUPLICATE_ENTRY")
        self.assertEqual(response_data["errors"][1]["message"], "Already Exist.")

        return True

    @staticmethod
    def invalid_data():
        """Return empty data to simulate missing required fields."""
        return {}

    def test_tenant_invalid_data(self):
        """Test tenant creation with missing required fields."""
        data = self.invalid_data()
        response = self.client.post(self.path, data=data)
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "tenant_code")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "tenant_name")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    @staticmethod
    def none_blank_data():
        """Return data with blank and null fields to trigger validation errors."""
        return {"tenant_code": " ", "tenant_name": None}

    def test_tenant_none_blank_invalid_data(self):
        """Test tenant creation with blank and null field values."""
        data = self.none_blank_data()
        response = self.client.post(self.path, data=data)
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "tenant_code")
        self.assertEqual(response_data["errors"][0]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field may not be blank."
        )

        self.assertEqual(response_data["errors"][1]["field"], "tenant_name")
        self.assertEqual(response_data["errors"][1]["code"], "NULL")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field may not be null."
        )

        return True

    def test_list_tenant_data(self):
        """Test listing tenants after creation."""
        self.test_tenant_create()

        response = self.client.get(self.path)
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("list", response_data["data"])
        self.assertIn("pagination", response_data["data"])

        self.assertEqual(len(response_data["data"]["list"]), 1)

        self.assertEqual(response_data["data"]["list"][0]["tenant_code"], "test")
        self.assertEqual(response_data["data"]["list"][0]["tenant_name"], "Test Tenant")
        self.assertIn("tenant_id", response_data["data"]["list"][0])

        self.assertEqual(response_data["data"]["pagination"]["count"], 1)
        self.assertEqual(response_data["data"]["pagination"]["page_size"], 10)
        self.assertEqual(response_data["data"]["pagination"]["current_page"], 1)
        self.assertEqual(response_data["data"]["pagination"]["total_pages"], 1)

        return True

    def test_tenant_no_data_found_list(self):
        """Test listing tenants when no tenant exists."""
        response = self.client.get(self.path)
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_get_tenant(self):
        """Test retrieving a single tenant by its UUID."""
        data = tenant_success_data()
        tenant = self.test_tenant_create()

        response = self.client.get(self.path_id.format(tenant_id=tenant["tenant_id"]))
        response_data = response.json()

        self.success_ok_200(response_data)

        self.assertIn("tenant_id", response_data["data"])
        self.assertEqual(response_data["data"]["tenant_code"], data["tenant_code"])
        self.assertEqual(response_data["data"]["tenant_name"], data["tenant_name"])

        return True

    def test_tenant_not_found_with_pk(self):
        """Test retrieving a tenant with an invalid UUID returns 404."""
        not_available_uuid = get_uuid()
        response = self.client.get(self.path_id.format(tenant_id=not_available_uuid))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    @staticmethod
    def update_success_data():
        """Return valid tenant data for update operations."""
        return {"tenant_code": "U-TC", "tenant_name": "U-TN"}

    def test_update_tenant(self):
        """Test successful tenant update via PUT."""
        data = self.update_success_data()

        tenant = self.test_tenant_create()
        response = self.client.put(
            self.path_id.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)

        self.assertIn("tenant_id", response_data["data"])
        self.assertEqual(response_data["data"]["tenant_code"], "U-TC")
        self.assertEqual(response_data["data"]["tenant_name"], "U-TN")

        return True

    def test_update_tenant_not_found(self):
        """Test updating a non-existent tenant returns 404."""
        data = self.update_success_data()

        not_available_uuid = get_uuid()

        response = self.client.put(
            self.path_id.format(tenant_id=not_available_uuid), data=data
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_update_tenant_invalid_data(self):
        """Test updating a tenant with missing required fields."""
        data = self.invalid_data()
        tenant = self.test_tenant_create()
        response = self.client.put(
            self.path_id.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "tenant_code")
        self.assertEqual(response_data["errors"][0]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field is required."
        )

        self.assertEqual(response_data["errors"][1]["field"], "tenant_name")
        self.assertEqual(response_data["errors"][1]["code"], "REQUIRED")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field is required."
        )

        return True

    def test_update_tenant_none_blank_invalid_data(self):
        """Test updating a tenant with blank and null fields."""
        data = self.none_blank_data()

        tenant = self.test_tenant_create()
        response = self.client.put(
            self.path_id.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "tenant_code")
        self.assertEqual(response_data["errors"][0]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field may not be blank."
        )

        self.assertEqual(response_data["errors"][1]["field"], "tenant_name")
        self.assertEqual(response_data["errors"][1]["code"], "NULL")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field may not be null."
        )

        return True

    def test_patch_tenant(self):
        """Test partial update of tenant using PATCH."""
        data = self.update_success_data()

        tenant = self.test_tenant_create()
        response = self.client.patch(
            self.path_id.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.update_success_ok_200(response_data)

        self.assertIn("tenant_id", response_data["data"])
        self.assertEqual(response_data["data"]["tenant_code"], "U-TC")
        self.assertEqual(response_data["data"]["tenant_name"], "U-TN")

        return True

    def test_patch_tenant_not_found(self):
        """Test patching a non-existent tenant returns 404."""
        data = self.update_success_data()

        not_available_uuid = get_uuid()

        response = self.client.patch(
            self.path_id.format(tenant_id=not_available_uuid), data=data
        )
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True

    def test_patch_tenant_invalid_data(self):
        """Test patching a tenant with missing data returns validation error."""
        data = self.invalid_data()
        tenant = self.test_tenant_create()
        response = self.client.patch(
            self.path_id.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.patch_data_not_provided_400(response_data)

        return True

    def test_patch_tenant_none_blank_invalid_data(self):
        """Test patching a tenant with blank and null field values."""
        data = self.none_blank_data()

        tenant = self.test_tenant_create()
        response = self.client.patch(
            self.path_id.format(tenant_id=tenant["tenant_id"]), data=data
        )
        response_data = response.json()

        self.bad_request_404(response_data)

        self.assertEqual(len(response_data["errors"]), 2)

        self.assertEqual(response_data["errors"][0]["field"], "tenant_code")
        self.assertEqual(response_data["errors"][0]["code"], "BLANK")
        self.assertEqual(
            response_data["errors"][0]["message"], "This field may not be blank."
        )

        self.assertEqual(response_data["errors"][1]["field"], "tenant_name")
        self.assertEqual(response_data["errors"][1]["code"], "NULL")
        self.assertEqual(
            response_data["errors"][1]["message"], "This field may not be null."
        )

        return True

    def test_delete_tenant(self):
        """Test successful deletion of a tenant."""
        tenant = self.test_tenant_create()

        response = self.client.delete(
            self.path_id.format(tenant_id=tenant["tenant_id"])
        )
        self.delete_success_204(response.status_code)

        return True

    def test_delete_tenant_not_found(self):
        """Test deletion of non-existent tenant returns 404."""
        not_available_uuid = get_uuid()

        response = self.client.delete(self.path_id.format(tenant_id=not_available_uuid))
        response_data = response.json()

        self.data_not_found_404(response_data)

        return True
